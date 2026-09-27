# pwa/api.py
"""
ArtForge HTTP API —— 把 main.py / skills 的功能包成 REST 接口

功能：
  - 生图（原有）
  - 鉴赏（图片 → 文章 → Word/PDF/HTML/富文本）
  - 排版（Markdown → 微信 HTML）
  - 一键流水线（生图 + 鉴赏 + 排版）
  - 浮世绘转换
  - 配置读取/更新
"""

from __future__ import annotations

import asyncio
import base64
import io
import os
import secrets
import sys
import uuid
import logging
import traceback
from pathlib import Path
from datetime import datetime
from typing import Optional, List

from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form
from fastapi.responses import FileResponse, Response
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
    load_dotenv(_env if _env.exists() else None)
except ImportError:
    pass


# ============================================================
# 日志
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("artforge.api")


# ============================================================
# FastAPI
# ============================================================

app = FastAPI(title="ArtForge API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)


# ============================================================
# 访问密码（HTTP Basic Auth）
# ============================================================

_PWA_USER = os.getenv("PWA_USERNAME", "").strip()
_PWA_PASS = os.getenv("PWA_PASSWORD", "").strip()

if _PWA_USER and _PWA_PASS:
    logger.info("访问鉴权已启用（保护 /api/*）")

    @app.middleware("http")
    async def _basic_auth(request: Request, call_next):
        path = request.url.path

        # 白名单
        if (path in ("/api/health", "/api/login")
                or path.startswith("/api/image/")
                or path.startswith("/api/curate/download/")
                or path.startswith("/api/format/download/")
                or path.startswith("/api/pipeline/download/")
                or path.startswith("/api/ukiyoe/image/")
                or not path.startswith("/api/")):
            return await call_next(request)

        auth = request.headers.get("authorization", "")
        if not auth.startswith("Basic "):
            return Response("需要登录", status_code=401,
                            headers={"WWW-Authenticate": 'Basic realm="ArtForge"'})
        try:
            decoded = base64.b64decode(auth[6:]).decode("utf-8")
            user, _, pwd = decoded.partition(":")
            if not (secrets.compare_digest(user.encode(), _PWA_USER.encode())
                    and secrets.compare_digest(pwd.encode(), _PWA_PASS.encode())):
                raise ValueError("bad")
        except Exception:
            return Response("用户名或密码错误", status_code=401,
                            headers={"WWW-Authenticate": 'Basic realm="ArtForge"'})
        return await call_next(request)
else:
    logger.warning("未设置 PWA_USERNAME/PWA_PASSWORD，公网暴露时无鉴权！")


class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/api/login")
def api_login(req: LoginRequest):
    if not (_PWA_USER and _PWA_PASS):
        return {"ok": True, "need_auth": False}
    ok_user = secrets.compare_digest(req.username.encode(), _PWA_USER.encode())
    ok_pass = secrets.compare_digest(req.password.encode(), _PWA_PASS.encode())
    if ok_user and ok_pass:
        return {"ok": True, "need_auth": True}
    raise HTTPException(401, "用户名或密码错误")


# ============================================================
# 内存任务表
# ============================================================

TASKS: dict = {}
CURATE_TASKS: dict = {}
FORMAT_TASKS: dict = {}
PIPELINE_TASKS: dict = {}
UKIYOE_TASKS: dict = {}


def _new_task(store: dict, kind: str = "") -> str:
    tid = uuid.uuid4().hex
    store[tid] = {
        "status": "pending", "progress": 0, "message": "排队中…",
        "result": None, "error": None, "kind": kind,
        "created_at": datetime.now().isoformat(),
    }
    return tid


def _task_response(store: dict, tid: str):
    t = store.get(tid)
    if not t:
        raise HTTPException(404, "task not found")
    return {"status": t["status"], "progress": t["progress"],
            "message": t["message"], "error": t.get("error"),
            "result": t["result"]}


# ============================================================
# ---------- 通用 ----------
# ============================================================

@app.get("/api/health")
def health():
    return {"ok": True, "service": "ArtForge", "version": "2.0.0"}


@app.get("/api/presets")
def list_presets():
    try:
        from core.prompt_builder import PromptBuilder
        return PromptBuilder().list_presets()
    except Exception as e:
        logger.error(f"list_presets 失败: {e}")
        raise HTTPException(500, str(e))


@app.get("/api/engines")
def list_engines():
    return {"engines": [
        {"id": "pollinations", "name": "Pollinations（免费）"},
        {"id": "agnes", "name": "Agnes AI（需 Key）"},
        {"id": "siliconflow", "name": "硅基流动（需 Key）"},
    ]}


# ============================================================
# ---------- 生图 ----------
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


@app.post("/api/generate")
async def generate(req: GenerateRequest):
    tid = _new_task(TASKS, "generate")
    asyncio.create_task(_run_generate(tid, req))
    return {"task_id": tid}


@app.get("/api/task/{task_id}")
def task_status(task_id: str):
    return _task_response(TASKS, task_id)


@app.get("/api/image/{task_id}")
def get_image(task_id: str):
    t = TASKS.get(task_id)
    if not t or t["status"] != "done":
        raise HTTPException(404, "not ready")
    path = Path(t["result"]["image_path"])
    if not path.exists():
        raise HTTPException(404, "image missing")
    return FileResponse(path, media_type="image/png",
                        filename=f"{t['result']['preset']}.png")


async def _run_generate(tid: str, req: GenerateRequest):
    t = TASKS[tid]

    def P(p, msg=""):
        t["progress"] = p
        if msg: t["message"] = msg

    try:
        from core.prompt_builder import PromptBuilder
        from core.safety import check_safety
        from api_engines import create_engine
        from compose_artwork import (
            InscriptionRenderer, pick_size, theme_from_preset,
            load_config, ARTIST_NAME,
        )

        t["status"] = "running"
        P(3, "准备中…")

        builder = PromptBuilder()
        if req.custom_prompt:
            prompt = req.custom_prompt
            detail = {"subject": req.custom_prompt, "composition": req.composition}
            theme = "通用"
        elif req.preset:
            prompt, detail = builder.compose_preset(
                req.preset, category=req.category, return_detail=True)
            theme = theme_from_preset(req.preset, req.category)
        else:
            prompt, detail = builder.compose_random(return_detail=True)
            theme = "通用"

        comp_map = {
            "vertical": "vertical hanging scroll, kakemono",
            "horizontal": "horizontal handscroll, emaki",
            "byobu": "folding screen, byobu, multi-panel",
            "fan": "round fan, circular composition",
            "album": "square album leaf",
        }
        detail["composition"] = comp_map.get(req.composition, comp_map["vertical"])
        detail.pop("inscription", None)
        prompt = ", ".join(detail[k] for k in builder.LAYER_ORDER if detail.get(k))

        negative = req.custom_negative or (
            f"{builder.get_negative()}, "
            "calligraphy, text, chinese characters, japanese text, "
            "kanji, kana, seal, stamp, signature, inscription, "
            "poem text, red seal, watermark, logo, letters, words"
        )

        is_safe, reason = check_safety(prompt, detail.get("style", ""),
                                       detail.get("subject", ""))
        if not is_safe:
            t["status"] = "error"; t["error"] = reason; return
        P(8, "prompt 就绪")

        width, height = pick_size(detail)
        P(15, f"调用 {req.engine} 出图…")
        loop = asyncio.get_event_loop()
        engine = create_engine(req.engine, load_config())

        image = await loop.run_in_executor(None, lambda: engine.generate_single(
            prompt=prompt, negative=negative,
            width=width, height=height, seed=req.seed))
        if image.mode != "RGBA": image = image.convert("RGBA")
        P(45, "出图完成")

        if req.use_aging:
            P(50, "做旧…")
            try:
                from services.aging_processor import AgingProcessor
                image = await loop.run_in_executor(None, lambda:
                    AgingProcessor(seed=req.seed).apply(
                        image.convert("RGB"), texture="xuan_paper",
                        strength=0.55).convert("RGBA"))
            except Exception as e:
                logger.warning(f"做旧失败: {e}")

        inscription_text = ""
        if req.use_inscription:
            P(58, "题词…")
            try:
                from services.inscription_generator import InscriptionGenerator
                def _gen():
                    ig = InscriptionGenerator(seed=req.seed)
                    lang = None if req.language == "auto" else req.language
                    text, _ = ig.generate(
                        theme=theme, format="auto", return_meta=True,
                        backend=req.engine if req.engine in ("agnes", "pollinations") else "auto",
                        category=req.category, language=lang)
                    return text
                inscription_text = await loop.run_in_executor(None, _gen)
                renderer = InscriptionRenderer()
                fs = max(24, int(min(width, height) * 0.045))
                image = renderer.render(image, inscription_text, font_size=fs,
                                        color=(45, 40, 35), position="top_right",
                                        margin=int(min(width, height) * 0.055),
                                        max_chars_per_col=8)
            except Exception as e:
                logger.warning(f"题词失败: {e}")

        if req.use_seal:
            P(70, "盖章…")
            try:
                from services.seal_generator import SealGenerator
                image = SealGenerator().apply_scheme(
                    image, ARTIST_NAME, scheme=req.seal_scheme, margin_ratio=0.05)
            except Exception as e:
                logger.warning(f"印章失败: {e}")

        if req.use_scroll:
            P(80, "装裱…")
            try:
                from services.scroll_composer import ScrollComposer
                image = await loop.run_in_executor(None, lambda:
                    ScrollComposer(seed=req.seed).compose(
                        image.convert("RGB"), composition=req.composition).convert("RGBA"))
            except Exception as e:
                logger.warning(f"装裱失败: {e}")

        if req.use_watermark:
            P(88, "水印…")
            try:
                from services.watermark import WatermarkProcessor
                image = WatermarkProcessor(seed=req.seed).add_subtle_watermark(
                    image, text=ARTIST_NAME, opacity=30, font_size=40,
                    angle=-30, spacing_x=180, spacing_y=180)
                if image.mode != "RGBA": image = image.convert("RGBA")
            except Exception as e:
                logger.warning(f"水印失败: {e}")

        P(95, "保存…")
        out_dir = PROJECT_ROOT / "output" / req.category
        out_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = req.preset or "random"
        out_path = out_dir / f"{name}_{ts}.png"
        image.convert("RGB").save(out_path, quality=95)

        t["result"] = {
            "image_path": str(out_path),
            "prompt": prompt, "theme": theme,
            "inscription": inscription_text,
            "seed": req.seed, "category": req.category,
            "preset": req.preset or "random",
            "engine": req.engine, "composition": req.composition,
            "width": image.size[0], "height": image.size[1],
        }
        t["status"] = "done"; P(100, "完成")
        logger.info(f"[{tid[:8]}] 生图完成: {out_path}")

    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"[{tid[:8]}] 生图失败: {e}\n{tb}")
        t["status"] = "error"; t["error"] = str(e); t["traceback"] = tb


# ============================================================
# ---------- 鉴赏 ----------
# ============================================================

@app.get("/api/curate/dirs")
def curate_dirs():
    """列出 output/ 下所有含图片的目录"""
    out = PROJECT_ROOT / "output"
    dirs = []
    if out.exists():
        for d in sorted(out.rglob("*")):
            if d.is_dir():
                imgs = list(d.glob("*.png")) + list(d.glob("*.jpg")) + list(d.glob("*.jpeg"))
                if imgs:
                    dirs.append({
                        "path": str(d.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                        "count": len(imgs),
                    })
    return {"dirs": dirs}


class CurateRequest(BaseModel):
    image_dir: str
    title: Optional[str] = None
    generate_html: bool = True
    generate_docx: bool = True
    generate_pdf: bool = True
    generate_clipboard: bool = True
    max_images: int = 100


@app.post("/api/curate")
async def curate(req: CurateRequest):
    tid = _new_task(CURATE_TASKS, "curate")
    asyncio.create_task(_run_curate(tid, req))
    return {"task_id": tid}


@app.get("/api/curate/task/{task_id}")
def curate_status(task_id: str):
    return _task_response(CURATE_TASKS, task_id)


@app.get("/api/curate/download/{task_id}/{kind}")
def curate_download(task_id: str, kind: str):
    t = CURATE_TASKS.get(task_id)
    if not t or t["status"] != "done":
        raise HTTPException(404, "not ready")
    r = t["result"]
    kind_map = {
        "md": ("md_path", "text/markdown", "article.md"),
        "html": ("html_path", "text/html", "article.html"),
        "docx": ("docx_path",
                 "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                 "article.docx"),
        "pdf": ("pdf_path", "application/pdf", "article.pdf"),
        "clipboard": ("clipboard_path", "text/html", "clipboard.html"),
    }
    if kind not in kind_map:
        raise HTTPException(400, "unknown kind")
    key, mime, fname = kind_map[kind]
    path = r.get(key)
    if not path or not Path(path).exists():
        raise HTTPException(404, f"{kind} not found")
    return FileResponse(path, media_type=mime, filename=fname)


async def _run_curate(tid: str, req: CurateRequest):
    t = CURATE_TASKS[tid]

    def P(p, msg=""):
        t["progress"] = p
        if msg: t["message"] = msg

    try:
        from skills.image_curator import ImageCurator

        t["status"] = "running"
        P(5, "初始化…")

        img_dir = Path(req.image_dir)
        if not img_dir.is_absolute():
            img_dir = PROJECT_ROOT / img_dir
        if not img_dir.exists():
            t["status"] = "error"; t["error"] = f"目录不存在: {img_dir}"; return

        P(10, "开始鉴赏（每张约 5-10 秒）…")
        loop = asyncio.get_event_loop()

        def _do():
            curator = ImageCurator({
                "generate_html": req.generate_html,
                "generate_docx": req.generate_docx,
                "generate_pdf": req.generate_pdf,
                "generate_clipboard": req.generate_clipboard,
                "max_images": req.max_images,
            })
            return curator.curate(str(img_dir), title=req.title or None)

        r = await loop.run_in_executor(None, _do)

        if r.get("status") != "success":
            t["status"] = "error"; t["error"] = r.get("error", "unknown"); return

        res = r["result"]
        t["result"] = {
            "md_path": res.get("article_path"),
            "html_path": res.get("html_path"),
            "docx_path": res.get("docx_path"),
            "pdf_path": res.get("pdf_path"),
            "clipboard_path": res.get("clipboard_path"),
            "article_dir": res.get("article_dir"),
            "title": res.get("title"),
            "image_count": res.get("image_count"),
        }
        t["status"] = "done"; P(100, "完成")
        logger.info(f"[{tid[:8]}] 鉴赏完成: {res.get('article_dir')}")

    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"[{tid[:8]}] 鉴赏失败: {e}\n{tb}")
        t["status"] = "error"; t["error"] = str(e); t["traceback"] = tb


# ============================================================
# ---------- 排版 ----------
# ============================================================

@app.get("/api/format/themes")
def format_themes():
    themes_dir = PROJECT_ROOT / "skills" / "wechat_formatter" / "themes"
    themes = sorted([f.stem for f in themes_dir.glob("*.json")])
    return {"themes": themes}


class FormatRequest(BaseModel):
    md_path: str
    theme: str = "newspaper"


@app.post("/api/format")
async def format_md(req: FormatRequest):
    tid = _new_task(FORMAT_TASKS, "format")
    asyncio.create_task(_run_format(tid, req))
    return {"task_id": tid}


@app.get("/api/format/task/{task_id}")
def format_status(task_id: str):
    return _task_response(FORMAT_TASKS, task_id)


@app.get("/api/format/download/{task_id}/{kind}")
def format_download(task_id: str, kind: str):
    t = FORMAT_TASKS.get(task_id)
    if not t or t["status"] != "done":
        raise HTTPException(404, "not ready")
    r = t["result"]
    kind_map = {
        "article": ("article_path", "text/html", "article.html"),
        "preview": ("preview_path", "text/html", "preview.html"),
    }
    if kind not in kind_map:
        raise HTTPException(400, "unknown kind")
    key, mime, fname = kind_map[kind]
    path = r.get(key)
    if not path or not Path(path).exists():
        raise HTTPException(404, f"{kind} not found")
    return FileResponse(path, media_type=mime, filename=fname)


async def _run_format(tid: str, req: FormatRequest):
    t = FORMAT_TASKS[tid]

    def P(p, msg=""):
        t["progress"] = p
        if msg: t["message"] = msg

    try:
        from skills.wechat_formatter import WechatFormatter

        t["status"] = "running"
        P(20, "排版中…")

        md_path = Path(req.md_path)
        if not md_path.is_absolute():
            md_path = PROJECT_ROOT / md_path
        if not md_path.exists():
            t["status"] = "error"; t["error"] = f"文件不存在: {md_path}"; return

        loop = asyncio.get_event_loop()

        def _do():
            fmt = WechatFormatter()
            return fmt.format(str(md_path), theme=req.theme, open=False)

        r = await loop.run_in_executor(None, _do)

        if r.get("status") != "success":
            t["status"] = "error"; t["error"] = r.get("error", "unknown"); return

        res = r["result"]
        t["result"] = {
            "article_path": res.get("article_path"),
            "preview_path": res.get("preview_path"),
            "article_dir": res.get("article_dir"),
            "title": res.get("title"),
            "theme": res.get("theme"),
            "word_count": res.get("word_count"),
        }
        t["status"] = "done"; P(100, "完成")
        logger.info(f"[{tid[:8]}] 排版完成: {res.get('article_dir')}")

    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"[{tid[:8]}] 排版失败: {e}\n{tb}")
        t["status"] = "error"; t["error"] = str(e); t["traceback"] = tb


# ============================================================
# ---------- 一键流水线 ----------
# ============================================================

class PipelineRequest(BaseModel):
    # 生图
    category: str = "yokai"
    preset: Optional[str] = None
    engine: str = "pollinations"
    composition: str = "vertical"
    seed: Optional[int] = None
    count: int = 3        # 生成几张
    # 鉴赏
    do_curate: bool = True
    curate_title: Optional[str] = None
    # 排版
    do_format: bool = True
    theme: str = "newspaper"


@app.post("/api/pipeline")
async def pipeline(req: PipelineRequest):
    tid = _new_task(PIPELINE_TASKS, "pipeline")
    asyncio.create_task(_run_pipeline(tid, req))
    return {"task_id": tid}


@app.get("/api/pipeline/task/{task_id}")
def pipeline_status(task_id: str):
    return _task_response(PIPELINE_TASKS, task_id)


@app.get("/api/pipeline/download/{task_id}/{kind}")
def pipeline_download(task_id: str, kind: str):
    t = PIPELINE_TASKS.get(task_id)
    if not t or t["status"] != "done":
        raise HTTPException(404, "not ready")
    r = t["result"]
    # kind 支持 md/docx/pdf/html/article/preview
    mapping = {
        "md": (r.get("md_path"), "text/markdown", "article.md"),
        "html": (r.get("html_path"), "text/html", "article.html"),
        "docx": (r.get("docx_path"),
                 "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                 "article.docx"),
        "pdf": (r.get("pdf_path"), "application/pdf", "article.pdf"),
        "clipboard": (r.get("clipboard_path"), "text/html", "clipboard.html"),
        "article": (r.get("article_path"), "text/html", "article.html"),
        "preview": (r.get("preview_path"), "text/html", "preview.html"),
    }
    if kind not in mapping:
        raise HTTPException(400, "unknown kind")
    path, mime, fname = mapping[kind]
    if not path or not Path(path).exists():
        raise HTTPException(404, f"{kind} not found")
    return FileResponse(path, media_type=mime, filename=fname)


async def _run_pipeline(tid: str, req: PipelineRequest):
    t = PIPELINE_TASKS[tid]

    def P(p, msg=""):
        t["progress"] = p
        if msg: t["message"] = msg

    try:
        t["status"] = "running"
        P(2, "开始流水线…")

        from core.prompt_builder import PromptBuilder
        from api_engines import create_engine
        from compose_artwork import (
            InscriptionRenderer, pick_size, theme_from_preset,
            load_config, ARTIST_NAME,
        )

        # ---------- 1. 生图 ----------
        # 输出目录
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir = PROJECT_ROOT / "output" / "daily" / f"{ts}_images"
        out_dir.mkdir(parents=True, exist_ok=True)

        builder = PromptBuilder()
        engine = create_engine(req.engine, load_config())

        total = max(1, req.count)
        produced = []

        for i in range(total):
            P(int(2 + i * 45 / total), f"生图 {i+1}/{total}…")

            try:
                if req.preset:
                    prompt, detail = builder.compose_preset(
                        req.preset, category=req.category, return_detail=True)
                    theme = theme_from_preset(req.preset, req.category)
                else:
                    prompt, detail = builder.compose_random(return_detail=True)
                    theme = "通用"

                comp_map = {
                    "vertical": "vertical hanging scroll, kakemono",
                    "horizontal": "horizontal handscroll, emaki",
                    "byobu": "folding screen, byobu, multi-panel",
                    "fan": "round fan, circular composition",
                    "album": "square album leaf",
                }
                detail["composition"] = comp_map.get(req.composition, comp_map["vertical"])
                detail.pop("inscription", None)
                prompt = ", ".join(detail[k] for k in builder.LAYER_ORDER if detail.get(k))
                negative = builder.get_negative() + (
                    ", calligraphy, text, chinese characters, seal, stamp, signature, watermark")

                width, height = pick_size(detail)
                loop = asyncio.get_event_loop()
                image = await loop.run_in_executor(None, lambda: engine.generate_single(
                    prompt=prompt, negative=negative,
                    width=width, height=height, seed=req.seed))
                if image.mode != "RGBA": image = image.convert("RGBA")

                # 做旧
                try:
                    from services.aging_processor import AgingProcessor
                    image = await loop.run_in_executor(None, lambda:
                        AgingProcessor(seed=req.seed).apply(
                            image.convert("RGB"), texture="xuan_paper",
                            strength=0.55).convert("RGBA"))
                except Exception: pass

                # 题词
                try:
                    from services.inscription_generator import InscriptionGenerator
                    def _gen():
                        ig = InscriptionGenerator(seed=req.seed)
                        text, _ = ig.generate(
                            theme=theme, format="auto", return_meta=True,
                            backend=req.engine if req.engine in ("agnes", "pollinations") else "auto",
                            category=req.category, language=None)
                        return text
                    inscription_text = await loop.run_in_executor(None, _gen)
                    renderer = InscriptionRenderer()
                    fs = max(24, int(min(width, height) * 0.045))
                    image = renderer.render(image, inscription_text, font_size=fs,
                                            color=(45, 40, 35), position="top_right",
                                            margin=int(min(width, height) * 0.055),
                                            max_chars_per_col=8)
                except Exception: pass

                # 印章
                try:
                    from services.seal_generator import SealGenerator
                    image = SealGenerator().apply_scheme(
                        image, ARTIST_NAME, scheme="contrast", margin_ratio=0.05)
                except Exception: pass

                # 装裱
                try:
                    from services.scroll_composer import ScrollComposer
                    image = await loop.run_in_executor(None, lambda:
                        ScrollComposer(seed=req.seed).compose(
                            image.convert("RGB"), composition=req.composition).convert("RGBA"))
                except Exception: pass

                # 保存
                p = out_dir / f"作品{i+1:02d}.png"
                image.convert("RGB").save(p, quality=95)
                produced.append(str(p))

            except Exception as e:
                logger.warning(f"第 {i+1} 张失败: {e}")
                continue

        if not produced:
            t["status"] = "error"; t["error"] = "未生成任何图片"; return

        P(50, f"生图完成 {len(produced)}/{total}")

        result = {
            "image_dir": str(out_dir),
            "images": produced,
            "count": len(produced),
        }

        # ---------- 2. 鉴赏 ----------
        if req.do_curate:
            P(55, "鉴赏中…")
            try:
                from skills.image_curator import ImageCurator
                def _curate():
                    curator = ImageCurator({
                        "generate_html": True, "generate_docx": True,
                        "generate_pdf": True, "generate_clipboard": True,
                    })
                    return curator.curate(str(out_dir), title=req.curate_title or None)
                r = await loop.run_in_executor(None, _curate)
                if r.get("status") == "success":
                    res = r["result"]
                    result.update({
                        "md_path": res.get("article_path"),
                        "html_path": res.get("html_path"),
                        "docx_path": res.get("docx_path"),
                        "pdf_path": res.get("pdf_path"),
                        "clipboard_path": res.get("clipboard_path"),
                        "article_dir": res.get("article_dir"),
                    })
                    P(80, "鉴赏完成")
                else:
                    logger.warning(f"鉴赏失败: {r.get('error')}")
            except Exception as e:
                logger.warning(f"鉴赏异常: {e}")

        # ---------- 3. 排版 ----------
        if req.do_format and result.get("md_path"):
            P(85, "排版中…")
            try:
                from skills.wechat_formatter import WechatFormatter
                def _format():
                    fmt = WechatFormatter()
                    return fmt.format(result["md_path"], theme=req.theme, open=False)
                fr = await loop.run_in_executor(None, _format)
                if fr.get("status") == "success":
                    res = fr["result"]
                    result.update({
                        "article_path": res.get("article_path"),
                        "preview_path": res.get("preview_path"),
                        "wechat_dir": res.get("article_dir"),
                    })
                    P(98, "排版完成")
                else:
                    logger.warning(f"排版失败: {fr.get('error')}")
            except Exception as e:
                logger.warning(f"排版异常: {e}")

        t["result"] = result
        t["status"] = "done"; P(100, "全部完成")
        logger.info(f"[{tid[:8]}] 流水线完成")

    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"[{tid[:8]}] 流水线失败: {e}\n{tb}")
        t["status"] = "error"; t["error"] = str(e); t["traceback"] = tb


# ============================================================
# ---------- 浮世绘 ----------
# ============================================================

@app.get("/api/ukiyoe/dirs")
def ukiyoe_dirs():
    out = PROJECT_ROOT / "output"
    dirs = []
    if out.exists():
        for d in sorted(out.rglob("*")):
            if d.is_dir():
                imgs = list(d.glob("*.png")) + list(d.glob("*.jpg")) + list(d.glob("*.jpeg"))
                if imgs:
                    dirs.append({
                        "path": str(d.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                        "count": len(imgs),
                    })
    return {"dirs": dirs}


class UkiyoeRequest(BaseModel):
    image_dir: str
    engine: str = "pollinations"
    strength: float = 0.75
    seal_text: str = "東方藝術"
    max_images: int = 10


@app.post("/api/ukiyoe")
async def ukiyoe(req: UkiyoeRequest):
    tid = _new_task(UKIYOE_TASKS, "ukiyoe")
    asyncio.create_task(_run_ukiyoe(tid, req))
    return {"task_id": tid}


@app.get("/api/ukiyoe/task/{task_id}")
def ukiyoe_status(task_id: str):
    return _task_response(UKIYOE_TASKS, task_id)


async def _run_ukiyoe(tid: str, req: UkiyoeRequest):
    t = UKIYOE_TASKS[tid]

    def P(p, msg=""):
        t["progress"] = p
        if msg: t["message"] = msg

    try:
        from skills.ukiyoe_converter import UkiyoeConverter

        t["status"] = "running"
        P(5, "初始化…")

        img_dir = Path(req.image_dir)
        if not img_dir.is_absolute():
            img_dir = PROJECT_ROOT / img_dir
        if not img_dir.exists():
            t["status"] = "error"; t["error"] = f"目录不存在: {img_dir}"; return

        # 收集图片
        exts = (".png", ".jpg", ".jpeg", ".webp", ".bmp")
        images = sorted([p for p in img_dir.iterdir()
                        if p.is_file() and p.suffix.lower() in exts])
        images = images[:req.max_images]
        if not images:
            t["status"] = "error"; t["error"] = "目录里没有图片"; return

        # 输出目录
        out_dir = img_dir.parent / f"{img_dir.name}_ukiyoe"
        out_dir.mkdir(parents=True, exist_ok=True)

        loop = asyncio.get_event_loop()
        produced = []

        for i, img_path in enumerate(images):
            P(int(10 + i * 80 / len(images)), f"转换 {i+1}/{len(images)}…")

            def _conv(p):
                conv = UkiyoeConverter()
                out_file = out_dir / f"{p.stem}_ukiyoe.png"
                return conv.convert(
                    image_path=str(p),
                    output_path=str(out_file),
                    engine_name=req.engine,
                    strength=req.strength,
                    seal_text=req.seal_text,
                )

            r = await loop.run_in_executor(None, _conv, img_path)
            if r.get("status") == "success":
                produced.append(r["result"]["output_path"])
            else:
                logger.warning(f"转换失败 {img_path.name}: {r.get('error')}")

        t["result"] = {
            "output_dir": str(out_dir),
            "images": produced,
            "count": len(produced),
            "total": len(images),
        }
        t["status"] = "done"; P(100, "完成")
        logger.info(f"[{tid[:8]}] 浮世绘完成: {len(produced)}/{len(images)}")

    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"[{tid[:8]}] 浮世绘失败: {e}\n{tb}")
        t["status"] = "error"; t["error"] = str(e); t["traceback"] = tb


@app.get("/api/ukiyoe/image/{task_id}")
def ukiyoe_image(task_id: str, idx: int = 0):
    """按索引返回转换后的某张图"""
    t = UKIYOE_TASKS.get(task_id)
    if not t or t["status"] != "done":
        raise HTTPException(404, "not ready")
    images = t["result"]["images"]
    if idx < 0 or idx >= len(images):
        raise HTTPException(404, "index out of range")
    return FileResponse(images[idx], media_type="image/png")


# ============================================================
# ---------- 配置 ----------
# ============================================================

@app.get("/api/config")
def get_config():
    """
    读取 .env（严格脱敏）
    - 敏感字段（KEY/SECRET/TOKEN/PASSWORD）：只显示 "已配置" / "未配置"
    - URL 字段：如果包含 token 也隐藏
    - 其他字段正常显示
    - 隐藏的 KEY 用户无法通过 API 获取原值
    """
    SENSITIVE_KEYWORDS = (
        "KEY", "SECRET", "TOKEN", "PASSWORD", "PASSWD",
        "CREDENTIAL", "AUTH", "COOKIE", "SESSION",
    )

    env_path = PROJECT_ROOT / ".env"
    cfg = {}
    if env_path.exists():
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            k = k.strip()
            v = v.strip()

            # 去掉可能的引号
            if (v.startswith('"') and v.endswith('"')) or \
               (v.startswith("'") and v.endswith("'")):
                v = v[1:-1]

            key_upper = k.upper()

            # 敏感字段：只显示状态
            if any(kw in key_upper for kw in SENSITIVE_KEYWORDS):
                if v:
                    # 只显示长度信息，不泄露任何字符
                    cfg[k] = f"***已配置（{len(v)} 字符）***"
                else:
                    cfg[k] = "（未配置）"
                continue

            # URL 里带敏感参数？简单检查
            if "URL" in key_upper and v:
                if any(kw in v.lower() for kw in ("token=", "key=", "secret=", "apikey=")):
                    cfg[k] = "***包含敏感参数的 URL 已隐藏***"
                    continue

            # 其他字段：如果值本身很长的十六进制/随机字符串，也隐藏
            if v and len(v) >= 24 and all(
                c in "0123456789abcdefABCDEF-_" for c in v
            ):
                cfg[k] = f"***疑似密钥（{len(v)} 字符）已隐藏***"
                continue

            cfg[k] = v

    # 按 key 排序，但敏感字段统一放最后
    def sort_key(kv):
        k = kv[0].upper()
        is_sensitive = any(kw in k for kw in SENSITIVE_KEYWORDS)
        return (is_sensitive, k)

    sorted_cfg = dict(sorted(cfg.items(), key=sort_key))
    return {"config": sorted_cfg}


# ============================================================
# 静态文件（放最后！）
# ============================================================

STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")