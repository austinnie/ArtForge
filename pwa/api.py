# pwa/api.py
"""
ArtForge HTTP API —— 把 main.py 的流水线包成 REST 接口，
供 PWA / 手机浏览器调用。

启动:
    python pwa/start_pwa.py
"""

from __future__ import annotations

import asyncio
import io
import os
import sys
import uuid
import base64
import secrets
import logging
import traceback
from pathlib import Path
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# ============================================================
# 项目路径 + .env
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from dotenv import load_dotenv
    _env = PROJECT_ROOT / ".env"
    if _env.exists():
        load_dotenv(_env)
    else:
        load_dotenv()
except ImportError:
    pass


from core.prompt_builder import PromptBuilder
from core.safety import check_safety
from api_engines import create_engine
from compose_artwork import (
    InscriptionRenderer,
    pick_size,
    theme_from_preset,
    load_config,
    ARTIST_NAME,
)


# ============================================================
# 日志
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("artforge.api")


# ============================================================
# FastAPI 应用
# ============================================================

app = FastAPI(title="ArtForge API", version="1.0.0")


# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# 访问密码（HTTP Basic Auth）
# 在 .env 里设置 PWA_USERNAME / PWA_PASSWORD 后自动启用
# 只保护 /api/*，静态资源放行（否则前端加载不出来）
# ============================================================

_PWA_USER = os.getenv("PWA_USERNAME", "").strip()
_PWA_PASS = os.getenv("PWA_PASSWORD", "").strip()

if _PWA_USER and _PWA_PASS:
    logger.info("访问鉴权已启用（保护 /api/*）")

    @app.middleware("http")
    async def _basic_auth(request: Request, call_next):
        path = request.url.path

        # 白名单：健康检查 + 登录接口 + 所有非 /api/ 路径（静态文件）
        if (
            path == "/api/health"
            or path == "/api/login"
            or not path.startswith("/api/")
        ):
            return await call_next(request)

        # 只拦 /api/*（除白名单外）
        auth = request.headers.get("authorization", "")
        if not auth.startswith("Basic "):
            return Response(
                "需要登录",
                status_code=401,
                headers={"WWW-Authenticate": 'Basic realm="ArtForge"'},
            )
        try:
            decoded = base64.b64decode(auth[6:]).decode("utf-8")
            user, _, pwd = decoded.partition(":")
            ok_user = secrets.compare_digest(
                user.encode(), _PWA_USER.encode())
            ok_pass = secrets.compare_digest(
                pwd.encode(), _PWA_PASS.encode())
            if not (ok_user and ok_pass):
                raise ValueError("bad")
        except Exception:
            return Response(
                "用户名或密码错误",
                status_code=401,
                headers={"WWW-Authenticate": 'Basic realm="ArtForge"'},
            )

        return await call_next(request)
else:
    logger.warning(
        "未设置 PWA_USERNAME/PWA_PASSWORD，公网暴露时无鉴权！"
    )


# ============================================================
# 登录接口（前端用）
# ============================================================

class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/api/login")
def api_login(req: LoginRequest):
    """前端登录：校验用户名密码，成功返回 ok"""
    if not (_PWA_USER and _PWA_PASS):
        # 没配密码 = 无需登录，直接放行
        return {"ok": True, "need_auth": False}
    ok_user = secrets.compare_digest(
        req.username.encode(), _PWA_USER.encode())
    ok_pass = secrets.compare_digest(
        req.password.encode(), _PWA_PASS.encode())
    if ok_user and ok_pass:
        return {"ok": True, "need_auth": True}
    raise HTTPException(401, "用户名或密码错误")

# ============================================================
# 内存任务表（简单版，重启即清空）
# ============================================================

TASKS: dict[str, dict] = {}


# ============================================================
# 请求模型
# ============================================================

class GenerateRequest(BaseModel):
    preset: Optional[str] = None
    category: str = "yokai"
    engine: str = "pollinations"
    composition: str = "vertical"
    seed: Optional[int] = None
    use_scroll: bool = True
    use_aging: bool = True
    use_inscription: bool = True
    use_seal: bool = True
    use_watermark: bool = True
    seal_scheme: str = "contrast"
    language: str = "auto"
    custom_prompt: Optional[str] = None
    custom_negative: Optional[str] = None


# ============================================================
# 路由
# ============================================================

@app.get("/api/health")
def health():
    return {"ok": True, "service": "ArtForge", "version": "1.0.0"}


@app.get("/api/presets")
def list_presets():
    """返回 {category: [preset1, preset2, ...]}"""
    try:
        builder = PromptBuilder()
        presets = builder.list_presets()
        return presets
    except Exception as e:
        logger.error(f"list_presets 失败: {e}")
        raise HTTPException(500, str(e))


@app.get("/api/engines")
def list_engines():
    """返回可用引擎列表"""
    return {
        "engines": [
            {"id": "pollinations", "name": "Pollinations（免费，无需 Key）"},
            {"id": "agnes",        "name": "Agnes AI（需 Key）"},
            {"id": "siliconflow",  "name": "硅基流动（需 Key）"},
        ]
    }


@app.post("/api/generate")
async def generate(req: GenerateRequest):
    """提交生成任务，立即返回 task_id"""
    task_id = uuid.uuid4().hex
    TASKS[task_id] = {
        "status": "pending",
        "progress": 0,
        "message": "排队中…",
        "result": None,
        "error": None,
        "created_at": datetime.now().isoformat(),
    }
    asyncio.create_task(_run_pipeline(task_id, req))
    return {"task_id": task_id}


@app.get("/api/task/{task_id}")
def task_status(task_id: str):
    if task_id not in TASKS:
        raise HTTPException(404, "task not found")
    t = TASKS[task_id]
    return {
        "status": t["status"],
        "progress": t["progress"],
        "message": t["message"],
        "error": t.get("error"),
        "result": t["result"],
    }


@app.get("/api/image/{task_id}")
def get_image(task_id: str):
    """返回成品图 PNG"""
    t = TASKS.get(task_id)
    if not t or t["status"] != "done":
        raise HTTPException(404, "not ready")
    path = Path(t["result"]["image_path"])
    if not path.exists():
        raise HTTPException(404, "image file missing")
    return FileResponse(path, media_type="image/png",
                        filename=f"{t['result']['preset']}.png")


@app.get("/api/meta/{task_id}")
def get_meta(task_id: str):
    t = TASKS.get(task_id)
    if not t or t["status"] != "done":
        raise HTTPException(404, "not ready")
    return t["result"]


# ============================================================
# 核心流水线（异步 + 进度上报）
# ============================================================

async def _run_pipeline(task_id: str, req: GenerateRequest):
    t = TASKS[task_id]

    def set_progress(p: int, msg: str = ""):
        t["progress"] = p
        if msg:
            t["message"] = msg

    try:
        t["status"] = "running"
        set_progress(3, "准备中…")

        builder = PromptBuilder()

        # ---------- 1. 组 prompt ----------
        if req.custom_prompt:
            prompt = req.custom_prompt
            detail = {
                "subject": req.custom_prompt,
                "composition": req.composition,
            }
            theme = "通用"
        elif req.preset:
            prompt, detail = builder.compose_preset(
                req.preset, category=req.category, return_detail=True,
            )
            theme = theme_from_preset(req.preset, req.category)
        else:
            prompt, detail = builder.compose_random(return_detail=True)
            theme = "通用"

        comp_map = {
            "vertical":   "vertical hanging scroll, kakemono",
            "horizontal": "horizontal handscroll, emaki",
            "byobu":      "folding screen, byobu, multi-panel",
            "fan":        "round fan, circular composition",
            "album":      "square album leaf",
        }
        detail["composition"] = comp_map.get(
            req.composition, comp_map["vertical"])
        detail.pop("inscription", None)
        parts = [detail[k] for k in builder.LAYER_ORDER if detail.get(k)]
        prompt = ", ".join(parts)

        # 负面提示词
        if req.custom_negative:
            negative = req.custom_negative
        else:
            negative = builder.get_negative()
            NO_TEXT = (
                "calligraphy, text, chinese characters, japanese text, "
                "kanji, kana, seal, stamp, signature, inscription, "
                "poem text, red seal, watermark, logo, letters, words"
            )
            negative = f"{negative}, {NO_TEXT}"

        # ---------- 2. 安全检查 ----------
        is_safe, reason = check_safety(
            prompt, detail.get("style", ""), detail.get("subject", ""),
        )
        logger.info(f"[{task_id[:8]}] 安全检查: {reason}")
        if not is_safe:
            t["status"] = "error"
            t["error"] = reason
            return

        set_progress(8, "prompt 就绪")

        # ---------- 3. 尺寸 ----------
        width, height = pick_size(detail)
        logger.info(f"[{task_id[:8]}] 尺寸: {width}x{height}")

        # ---------- 4. 出图 ----------
        set_progress(15, f"调用 {req.engine} 出图…")
        loop = asyncio.get_event_loop()

        config = load_config()
        engine = create_engine(req.engine, config)

        image = await loop.run_in_executor(
            None,
            lambda: engine.generate_single(
                prompt=prompt, negative=negative,
                width=width, height=height, seed=req.seed,
            ),
        )
        if image.mode != "RGBA":
            image = image.convert("RGBA")
        set_progress(45, "出图完成")

        # ---------- 5. 做旧 ----------
        if req.use_aging:
            set_progress(50, "做旧处理…")
            try:
                from services.aging_processor import AgingProcessor

                def _age():
                    return AgingProcessor(seed=req.seed).apply(
                        image.convert("RGB"),
                        texture="xuan_paper", strength=0.55,
                    ).convert("RGBA")

                image = await loop.run_in_executor(None, _age)
            except Exception as e:
                logger.warning(f"[{task_id[:8]}] 做旧失败: {e}")

        # ---------- 6. 题词 ----------
        inscription_text = ""
        if req.use_inscription:
            set_progress(58, "生成题词…")
            try:
                from services.inscription_generator import (
                    InscriptionGenerator,
                )

                def _gen_insc():
                    ig = InscriptionGenerator(seed=req.seed)
                    lang = None if req.language == "auto" else req.language
                    text, _ = ig.generate(
                        theme=theme, format="auto", return_meta=True,
                        backend=req.engine
                        if req.engine in ("agnes", "pollinations")
                        else "auto",
                        category=req.category, language=lang,
                    )
                    return text

                inscription_text = await loop.run_in_executor(
                    None, _gen_insc)

                renderer = InscriptionRenderer()
                fs = max(24, int(min(width, height) * 0.045))
                image = renderer.render(
                    image, inscription_text,
                    font_size=fs,
                    color=(45, 40, 35),
                    position="top_right",
                    margin=int(min(width, height) * 0.055),
                    max_chars_per_col=8,
                )
            except Exception as e:
                logger.warning(f"[{task_id[:8]}] 题词失败: {e}")

        # ---------- 7. 印章 ----------
        if req.use_seal:
            set_progress(70, "盖章…")
            try:
                from services.seal_generator import SealGenerator
                sg = SealGenerator()
                image = sg.apply_scheme(
                    image, ARTIST_NAME,
                    scheme=req.seal_scheme, margin_ratio=0.05,
                )
            except Exception as e:
                logger.warning(f"[{task_id[:8]}] 印章失败: {e}")

        # ---------- 8. 装裱 ----------
        if req.use_scroll:
            set_progress(80, "装裱…")
            try:
                from services.scroll_composer import ScrollComposer

                def _mount():
                    return ScrollComposer(seed=req.seed).compose(
                        image.convert("RGB"),
                        composition=req.composition,
                    ).convert("RGBA")

                image = await loop.run_in_executor(None, _mount)
            except Exception as e:
                logger.warning(f"[{task_id[:8]}] 装裱失败: {e}")

        # ---------- 9. 水印 ----------
        if req.use_watermark:
            set_progress(88, "加水印…")
            try:
                from services.watermark import WatermarkProcessor
                wp = WatermarkProcessor(seed=req.seed)
                image = wp.add_subtle_watermark(
                    image, text=ARTIST_NAME,
                    opacity=30, font_size=40,
                    angle=-30,
                    spacing_x=180, spacing_y=180,
                )
                if image.mode != "RGBA":
                    image = image.convert("RGBA")
            except Exception as e:
                logger.warning(f"[{task_id[:8]}] 水印失败: {e}")

        # ---------- 10. 保存 ----------
        set_progress(95, "保存中…")
        out_dir = PROJECT_ROOT / "output" / req.category
        out_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = req.preset or "random"
        out_path = out_dir / f"{name}_{ts}.png"
        image.convert("RGB").save(out_path, quality=95)

        meta_path = out_path.with_suffix(".txt")
        with open(meta_path, "w", encoding="utf-8") as f:
            f.write(f"preset: {name}\n")
            f.write(f"category: {req.category}\n")
            f.write(f"engine: {req.engine}\n")
            f.write(f"seed: {req.seed}\n")
            f.write(f"composition: {req.composition}\n")
            f.write(f"prompt:\n{prompt}\n\n")
            f.write(f"negative:\n{negative}\n")
            if inscription_text:
                f.write(f"\ninscription:\n{inscription_text}\n")

        t["result"] = {
            "image_path": str(out_path),
            "meta_path": str(meta_path),
            "prompt": prompt,
            "theme": theme,
            "inscription": inscription_text,
            "seed": req.seed,
            "category": req.category,
            "preset": req.preset or "random",
            "engine": req.engine,
            "composition": req.composition,
            "width": image.size[0],
            "height": image.size[1],
        }
        t["status"] = "done"
        set_progress(100, "完成")
        logger.info(f"[{task_id[:8]}] 完成: {out_path}")

    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"[{task_id[:8]}] 失败: {e}\n{tb}")
        t["status"] = "error"
        t["error"] = str(e)
        t["traceback"] = tb


# ============================================================
# 静态文件（PWA 前端）—— 必须放最后
# ============================================================

STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)

app.mount(
    "/",
    StaticFiles(directory=str(STATIC_DIR), html=True),
    name="static",
)


# ============================================================
# 直接运行入口
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")