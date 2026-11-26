# skills/artforge_daily/skill.py
"""
ArtForge 日更号 —— 智能调度与全渠道分发版 (v3.0)
重构亮点：
1. 引入 Context 模式，串联全流程
2. 解耦“内容生产”与“渠道分发”
3. 原生支持国内（公众号/视频号）与海外（IG/FB）多语言发布
"""
from __future__ import annotations

import argparse
import json
import logging
import random
import sys
import time
import traceback
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from dotenv import load_dotenv
    env_file = PROJECT_ROOT / ".env"
    load_dotenv(env_file if env_file.exists() else None)
except ImportError:
    pass

logger = logging.getLogger(__name__)

# ============================================================
# 🎯 全局配置与上下文
# ============================================================
PRESETS_DIR = PROJECT_ROOT / "presets"
HISTORY_FILE = PROJECT_ROOT / "output" / "daily_history.json"
AVOID_RECENT_DAYS = 7

DAILY_BLACKLIST = {
    "art_nude", "art_nude_explicit", "art_nude_modern", "art_nude_oriental",
    "war", "beast", "mythical", "astrology", "medicine"
}

DAILY_CATEGORY_POOL = {
    "tang": 4, "japanese": 4, "gufeng": 4, "genji": 3, "yokai": 3,
    "landscape": 3, "mountain": 2, "water": 2, "tree": 2, "flower": 2, 
    "bird": 2, "season": 2, "tea_ceremony": 2, "calligraphy": 2,
    "cat": 1, "folklore": 1, "modern": 1
}

WEEKLY_THEME_SCHEDULE = {
    0: ["tang", "genji", "dynasty"], 1: ["japanese", "yokai"], 
    2: ["gufeng", "landscape"], 3: ["flower", "bird", "cat"], 
    4: ["yokai_animals", "folklore"], 5: ["season", "festival"], 
    6: ["calligraphy", "tea_ceremony"]
}

EMOTION_MAP = {
    "tang": "epic", "genji": "epic", "dynasty": "epic", "japanese": "mysterious", 
    "yokai": "mysterious", "gufeng": "peaceful", "landscape": "peaceful", 
    "flower": "joyful", "tea_ceremony": "melancholic"
}

@dataclass
class PipelineContext:
    """贯穿整个流水线的上下文，避免参数满天飞"""
    category: str = ""
    presets: List[str] = field(default_factory=list)
    image_dir: Optional[Path] = None
    md_path: Optional[Path] = None
    article_dir: Optional[Path] = None
    video_path: Optional[Path] = None
    
    title_cn: str = ""
    title_en: str = ""
    intro_cn: str = ""
    desc_en: str = ""
    
    results: Dict[str, Any] = field(default_factory=dict)

# ============================================================
# 工具函数：预设与历史管理
# ============================================================
def list_categories() -> List[str]:
    if not PRESETS_DIR.exists(): return []
    return [d.name for d in sorted(PRESETS_DIR.iterdir()) if d.is_dir() and not d.name.startswith(".") and list(d.glob("*.py"))]

def list_presets(category: str) -> List[str]:
    d = PRESETS_DIR / category
    if not d.exists(): return []
    return sorted(f.stem for f in d.glob("*.py") if f.stem not in ("__init__",))

def _load_history() -> list:
    if HISTORY_FILE.exists():
        try: return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception: return []
    return []

def _save_history(history: list):
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(history[-30:], ensure_ascii=False, indent=2), encoding="utf-8")


class ArtForgeDaily:
    name = "artforge_daily"
    version = "3.0.0"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self._setup_logging()

    def _setup_logging(self):
        level = self.config.get("log_level", "INFO")
        logging.basicConfig(level=getattr(logging, level.upper()), format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # ==================== 核心阶段 1：智能选题 ====================
    def _select_topic(self, category: Optional[str], presets: Optional[List[str]], count: int, use_smart: bool, week_plan: bool, avoid_days: int) -> PipelineContext:
        ctx = PipelineContext()
        all_cats = list_categories()
        history = _load_history()
        recent_cats = set([h["category"] for h in history[-avoid_days:]])
        
        # 选分类
        if use_smart and not category:
            if week_plan:
                base_pool = WEEKLY_THEME_SCHEDULE.get(datetime.now().weekday(), list(DAILY_CATEGORY_POOL.keys()))
            else:
                base_pool = list(DAILY_CATEGORY_POOL.keys())
                
            valid_pool = {c: DAILY_CATEGORY_POOL.get(c, 1) for c in base_pool if c not in DAILY_BLACKLIST and c in all_cats and c not in recent_cats}
            if not valid_pool:
                valid_pool = {c: 1 for c in all_cats if c not in DAILY_BLACKLIST}
            
            ctx.category = random.choices(list(valid_pool.keys()), weights=list(valid_pool.values()), k=1)[0]
            logger.info(f"🎯 智能选中分类: {ctx.category}")
        else:
            ctx.category = category or random.choice([c for c in all_cats if c not in DAILY_BLACKLIST])

        # 选预设
        all_presets = list_presets(ctx.category)
        if use_smart and not presets:
            num = min(count, len(all_presets))
            ctx.presets = random.sample(all_presets, num)
            # 智能模式下，count 重置为 1，每预设生成一张
            self.config["count"] = 1
            logger.info(f"🎲 智能选中 {len(ctx.presets)} 个预设: {ctx.presets}")
        else:
            ctx.presets = presets or random.sample(all_presets, min(count, len(all_presets)))
            
        return ctx

    # ==================== 核心阶段 2：视觉生成 ====================
    def _generate_artwork(self, ctx: PipelineContext) -> None:
        from core.prompt_builder import PromptBuilder
        from core.safety import check_safety
        from api_engines import create_engine
        from compose_artwork import InscriptionRenderer, pick_size, theme_from_preset, load_config, ARTIST_NAME
        
        count = int(self.config.get("count", 1))
        engine_name = self.config.get("engine", "pollinations")
        composition = self.config.get("composition", "vertical")
        seed = self.config.get("seed")
        seal_scheme = self.config.get("seal_scheme", "contrast")
        language = self.config.get("language", "auto")
        
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        ctx.image_dir = PROJECT_ROOT / "output" / "daily" / f"{ts}_images"
        ctx.image_dir.mkdir(parents=True, exist_ok=True)

        builder = PromptBuilder()
        engine_obj = create_engine(engine_name, load_config())
        comp_map = {"vertical": "vertical hanging scroll", "horizontal": "horizontal handscroll", "byobu": "folding screen", "fan": "round fan", "album": "square album leaf"}
        
        total = len(ctx.presets) * count
        idx = 0
        
        for preset in ctx.presets:
            for i in range(count):
                idx += 1
                tag = f"{preset}_{i+1:02d}"
                try:
                    prompt, detail = builder.compose_preset(preset, category=ctx.category, return_detail=True)
                    theme = theme_from_preset(preset, ctx.category)
                    detail["composition"] = comp_map.get(composition, comp_map["vertical"])
                    detail.pop("inscription", None)
                    full_prompt = ", ".join(detail[k] for k in builder.LAYER_ORDER if detail.get(k))
                    
                    negative = builder.get_negative() + ", calligraphy, text, chinese characters, kanji, kana, seal, stamp, signature, watermark, logo"
                    if not check_safety(full_prompt, detail.get("style", ""), detail.get("subject", ""))[0]:
                        continue

                    width, height = pick_size(detail)
                    image = engine_obj.generate_single(prompt=full_prompt, negative=negative, width=width, height=height, seed=seed).convert("RGBA")

                    # 后期处理：做旧 -> 题词 -> 印章 -> 装裱 -> 水印
                    self._apply_post_processing(image, width, height, preset, ctx.category, theme, engine_name, seed, seal_scheme, language, ARTIST_NAME)
                    
                    out_path = ctx.image_dir / f"{preset}_{i+1:02d}.png"
                    image.convert("RGB").save(out_path, quality=95)
                    logger.info(f"  → 已生成 {out_path.name}")
                    
                    if idx < total: time.sleep(1.5)
                except Exception as e:
                    logger.error(f"{tag} 生成失败: {e}")

    def _apply_post_processing(self, image, width, height, preset, category, theme, engine_name, seed, seal_scheme, language, artist_name):
        """提取出的图片后期处理逻辑，保持主生图函数干净"""
        from compose_artwork import InscriptionRenderer
        
        # 1. 做旧
        try:
            from services.aging_processor import AgingProcessor
            image = AgingProcessor(seed=seed).apply(image.convert("RGB"), texture="xuan_paper", strength=0.55).convert("RGBA")
        except Exception as e: logger.warning(f"做旧失败: {e}")

        # 2. 题词
        try:
            from services.inscription_generator import InscriptionGenerator
            ig = InscriptionGenerator(seed=seed)
            lang = None if language == "auto" else language
            inscription_text, _ = ig.generate(theme=theme, format="auto", return_meta=True, backend=engine_name if engine_name in ("agnes", "pollinations") else "auto", category=category, language=lang)
            fs = max(24, int(min(width, height) * 0.045))
            image = InscriptionRenderer().render(image, inscription_text, font_size=fs, color=(45, 40, 35), position="top_right", margin=int(min(width, height) * 0.055), max_chars_per_col=8)
        except Exception as e: logger.warning(f"题词失败: {e}")

        # 3. 印章 & 装裱
        try:
            from services.seal_generator import SealGenerator
            image = SealGenerator().apply_scheme(image, artist_name, scheme=seal_scheme, margin_ratio=0.05)
        except Exception as e: logger.warning(f"印章失败: {e}")

        try:
            from services.scroll_composer import ScrollComposer
            image = ScrollComposer(seed=seed).compose(image.convert("RGB"), composition=self.config.get("composition", "vertical")).convert("RGBA")
        except Exception as e: logger.warning(f"装裱失败: {e}")

        # 4. 水印
        try:
            from services.watermark import WatermarkProcessor
            image = WatermarkProcessor(seed=seed).add_subtle_watermark(image, text=artist_name, opacity=30, font_size=40, angle=-30).convert("RGBA")
        except Exception as e: logger.warning(f"水印失败: {e}")

    # ==================== 核心阶段 3：文案与翻译 ====================
    def _generate_article(self, ctx: PipelineContext) -> None:
        from skills.image_curator import ImageCurator
        curator = ImageCurator({"generate_html": True, "generate_docx": False, "generate_pdf": False, "generate_clipboard": False})
        r = curator.curate(str(ctx.image_dir), title=None)
        if r.get("status") != "success": raise RuntimeError("文章生成失败")
        
        # 获取原始产物
        md_path = Path(r["result"]["article_path"])
        meta = json.loads((md_path.parent / "metadata.json").read_text(encoding="utf-8"))
        ctx.intro_cn = meta.get("intro", "")[:200]
        
        # 智能生成标题并重命名
        ctx.title_cn = self._generate_smart_title(ctx.intro_cn, ctx.category, ctx.presets) or f"{ctx.category.title()} · {datetime.now().strftime('%Y-%m-%d')}"
        ctx.md_path = self._update_article_title(md_path, ctx.title_cn)

    def _translate_for_social(self, text: str) -> str:
        try:
            from api_engines import create_engine
            from config.settings import settings
            engine = create_engine("agnes", {"AGNES_API_KEY": settings.agnes_api_key, "AGNES_BASE_URL": settings.agnes_base_url})
            prompt = f"You are an art curator on Instagram. Translate and rewrite this into an engaging English caption. Add 5-8 hashtags (e.g., #AsianArt #Ukiyoe). Only output the caption.\n\nChinese: {text}"
            return engine.chat_simple(prompt).strip()
        except Exception:
            return text

    # ==================== 核心阶段 4：排版与视频打包 ====================
    def _build_media(self, ctx: PipelineContext, targets: List[str]) -> None:
        # 1. 排版（仅当需要发公众号长文时）
        if "article" in targets:
            from skills.wechat_formatter import WechatFormatter
            fmt = WechatFormatter()
            kwargs = {"theme": self.config.get("theme", "newspaper"), "open": False}
            fp = self.config.get("footer_image")
            if fp and (PROJECT_ROOT / fp).exists():
                kwargs.update({"footer_image": str(PROJECT_ROOT / fp), "footer_alt": "关注"})
            
            r = fmt.format(str(ctx.md_path), **kwargs)
            if r.get("status") == "success": ctx.article_dir = Path(r["result"]["article_dir"])

        # 2. 合成视频（发视频号或 FB）
        if any(t in targets for t in ["video", "facebook"]):
            ctx.video_path = self._build_video(ctx.image_dir, ctx.title_cn)
            if ctx.video_path:
                ctx.title_en = self._translate_for_social(ctx.title_cn).split("\n")[0][:80]
                ctx.desc_en = self._translate_for_social(ctx.intro_cn)

    def _build_video(self, image_dir: Path, title: str) -> Optional[Path]:
        ffmpeg = shutil.which("ffmpeg")
        if not ffmpeg: 
            logger.error("未找到 ffmpeg")
            return None
            
        imgs = sorted([p for p in image_dir.iterdir() if p.suffix.lower() in (".png", ".jpg")])
        if not imgs: return None
        
        # 查找 BGM
        bgm = self.config.get("bgm")
        final_bgm = Path(bgm) if bgm and Path(bgm).exists() else None
        if not final_bgm:
            mp3s = list((PROJECT_ROOT / "assets" / "music").glob("*.mp3"))
            if mp3s: final_bgm = random.choice(mp3s)

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out = PROJECT_ROOT / "output" / "videos" / f"{ts}_{title[:10]}.mp4"
        out.parent.mkdir(parents=True, exist_ok=True)
        work = Path(tempfile.mkdtemp(prefix="af_video_"))

        try:
            segs = []
            for i, img in enumerate(imgs):
                seg = work / f"seg_{i:03d}.mp4"
                # 适配 1080x1920 竖屏
                vf = "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1,format=yuv420p"
                subprocess.run([ffmpeg, "-y", "-loop", "1", "-t", "4", "-i", str(img), "-vf", vf, "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "20", str(seg)], capture_output=True, check=True)
                segs.append(seg)
                
            concat = work / "concat.txt"
            concat.write_text("\n".join(f"file '{s.as_posix()}'" for s in segs), encoding="utf-8")
            merged = work / "merged.mp4"
            subprocess.run([ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(concat), "-c", "copy", str(merged)], capture_output=True, check=True)
            
            if final_bgm:
                subprocess.run([ffmpeg, "-y", "-i", str(merged), "-stream_loop", "-1", "-i", str(final_bgm), "-shortest", "-c:v", "copy", "-c:a", "aac", str(out)], capture_output=True, check=True)
            else:
                shutil.copy2(merged, out)
            return out
        finally:
            shutil.rmtree(work, ignore_errors=True)

    # ==================== 核心阶段 5：全渠道分发 ====================
    def _distribute(self, ctx: PipelineContext, targets: List[str]) -> None:
        from skills.social_auto_upload import SocialAutoUpload
        sau = SocialAutoUpload()
        cover = next(ctx.image_dir.glob("*.png"), None)

        for target in targets:
            logger.info(f"📤 准备分发到: {target}")
            try:
                if target == "article" and ctx.article_dir:
                    # 公众号长文
                    from skills.wechat_formatter import WechatFormatter
                    r = WechatFormatter().publish(str(ctx.article_dir), dry_run=self.config.get("dry_run", False))
                    ctx.results["push_article"] = {"ok": r.get("status") == "success"}

                elif target == "newspic":
                    # 公众号小绿书（贴图）
                    from skills.wechat_formatter.publisher import wechat_publish as wp
                    imgs = sorted([str(p) for p in ctx.image_dir.iterdir() if p.suffix.lower() in (".png", ".jpg")])[:20]
                    token = wp.get_access_token()
                    media_ids = wp.upload_images_as_material(token, imgs)
                    if media_ids:
                        mid = wp.push_draft(token, title=ctx.title_cn[:20], content=ctx.intro_cn, article_type="newspic", image_media_ids=media_ids)
                        ctx.results["push_newspic"] = {"ok": bool(mid)}

                elif target == "instagram":
                    # Instagram 轮播图
                    imgs = sorted([str(p) for p in ctx.image_dir.iterdir() if p.suffix.lower() in (".png", ".jpg")])[:10]
                    r = sau.publish_note(platform="instagram", images=imgs, title=ctx.title_en[:30], note=ctx.desc_en, account=self.config.get("ig_account", "default"))
                    ctx.results["push_instagram"] = {"ok": r.get("status") == "success"}

                elif target in ["video", "facebook"]:
                    # 视频号 或 Facebook 视频
                    plat = "tencent" if target == "video" else "facebook"
                    acc = self.config.get("video_account", "test") if plat == "tencent" else self.config.get("fb_account", "default")
                    title = ctx.title_cn if plat == "tencent" else ctx.title_en
                    desc = ctx.title_cn if plat == "tencent" else ctx.desc_en
                    
                    if ctx.video_path:
                        r = sau.publish_video(platform=plat, file=str(ctx.video_path), title=title, desc=desc, account=acc, thumbnail=str(cover) if cover else None)
                        ctx.results[f"push_{target}"] = {"ok": r.get("status") == "success"}
            except Exception as e:
                logger.error(f"❌ 分发到 {target} 失败: {e}")
                ctx.results[f"push_{target}"] = {"ok": False, "error": str(e)}

    # ==================== 🚀 主引擎入口 ====================
    def execute(self, **kwargs) -> Dict[str, Any]:
        start = time.time()
        logger.info(f"执行 {self.name} v{self.version}")
        self.config.update(kwargs) # 将 CLI 传入的参数合并进 config
        
        targets = kwargs.get("targets", ["newspic", "video"])
        
        try:
            # 1. 选题
            ctx = self._select_topic(
                category=kwargs.get("category"), presets=kwargs.get("presets"), 
                count=int(kwargs.get("count", 2)), use_smart=kwargs.get("smart", False),
                week_plan=kwargs.get("week_plan", False), avoid_days=int(kwargs.get("avoid_days", AVOID_RECENT_DAYS))
            )
            
            # 2. 生图
            self._generate_artwork(ctx)
            if not list(ctx.image_dir.glob("*.png")): raise RuntimeError("没有生成任何图片")

            # 3. 写文与翻译
            self._generate_article(ctx)

            # 4. 打包媒体
            self._build_media(ctx, targets)

            # 5. 分发
            self._distribute(ctx, targets)

            # 6. 记录历史
            if kwargs.get("smart", False):
                history = _load_history()
                history.append({"category": ctx.category, "presets": ctx.presets, "date": datetime.now().strftime("%Y-%m-%d %H:%M")})
                _save_history(history)

            return {
                "status": "success",
                "result": {
                    "category": ctx.category,
                    "image_dir": str(ctx.image_dir),
                    "md_path": str(ctx.md_path) if ctx.md_path else None,
                    "video_path": str(ctx.video_path) if ctx.video_path else None,
                    **ctx.results
                },
                "metadata": {"elapsed": f"{time.time() - start:.1f}s"}
            }
        except Exception as e:
            logger.error(f"执行失败: {e}")
            traceback.print_exc()
            return {"status": "error", "error": str(e)}

    # --- 辅助函数：生成标题与更新文件（省略部分重复代码，逻辑保持不变） ---
    def _generate_smart_title(self, intro: str, category: str, presets: list) -> Optional[str]:
        if not intro: return None
        try:
            from api_engines import create_engine
            from config.settings import settings
            engine = create_engine("agnes", {"AGNES_API_KEY": settings.agnes_api_key})
            prompt = f"你是资深艺术编辑。根据引言生成一个8-15字的诗意标题。只输出标题。\n分类：{category}\n引言：{intro}"
            res = engine.chat_simple(prompt).strip().strip('"').strip("「」")
            return res if 4 <= len(res) <= 20 else None
        except Exception:
            return None

    def _update_article_title(self, md_path: Path, new_title: str) -> Path:
        # 复用你之前的重命名和替换逻辑...
        try:
            article_dir = md_path.parent
            meta_file = article_dir / "metadata.json"
            if meta_file.exists():
                meta = json.loads(meta_file.read_text(encoding="utf-8"))
                meta["title"] = new_title
                meta_file.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
            
            if md_path.exists():
                lines = md_path.read_text(encoding="utf-8").split("\n")
                for i, line in enumerate(lines):
                    if line.startswith("# "): lines[i] = f"# {new_title}"; break
                md_path.write_text("\n".join(lines), encoding="utf-8")
                
            old_name = article_dir.name
            parts = old_name.split("_", 2)
            if len(parts) >= 3:
                new_path = article_dir.parent / f"{parts[0]}_{parts[1]}_{new_title}"
                if not new_path.exists():
                    article_dir.rename(new_path)
                    return new_path / "article.md"
        except Exception as e:
            logger.warning(f"更新标题异常: {e}")
        return md_path

# ============================================================
# CLI 入口
# ============================================================
def _cli():
    ap = argparse.ArgumentParser(description="ArtForge 日更号 (全渠道分发版)")
    
    # 核心参数
    ap.add_argument("--category", default=None)
    ap.add_argument("--presets", nargs="*", default=None)
    ap.add_argument("--count", type=int, default=2)
    ap.add_argument("--engine", default="agnes", choices=["pollinations", "agnes", "siliconflow"])
    
    # 调度参数
    ap.add_argument("--smart", action="store_true", help="启用智能调度")
    ap.add_argument("--week-plan", action="store_true", help="启用主题周计划")
    ap.add_argument("--avoid-days", type=int, default=AVOID_RECENT_DAYS)
    
    # 🌟 分发控制参数
    ap.add_argument("--targets", nargs="+", default=["newspic", "video"], 
                    choices=["article", "newspic", "video", "instagram", "facebook"],
                    help="指定要发布的平台，支持多选。如：--targets newspic instagram")
    
    # 账号配置
    ap.add_argument("--ig-account", default="default", help="Instagram 账号名")
    ap.add_argument("--fb-account", default="default", help="Facebook 账号名")
    ap.add_argument("--video-account", default="test", help="视频号账号名")
    ap.add_argument("--footer-image", default=None, help="公众号结尾图路径")
    
    # 调试
    ap.add_argument("--dry-run", action="store_true")

    args = ap.parse_args()

    # 兼容旧的 --no-article / --no-video 参数
    targets = args.targets
    if getattr(args, "no_article", False) and "article" in targets: targets.remove("article")
    if getattr(args, "no_video", False) and "video" in targets: targets.remove("video")

    pipe = ArtForgeDaily()
    r = pipe.execute(
        category=args.category, presets=args.presets, count=args.count,
        engine=args.engine, smart=args.smart, week_plan=args.week_plan, 
        avoid_days=args.avoid_days, targets=targets, 
        ig_account=args.ig_account, fb_account=args.fb_account, video_account=args.video_account,
        footer_image=args.footer_image, dry_run=args.dry_run
    )

    if r["status"] == "success":
        print("\n" + "=" * 72)
        print("  ✅ ArtForge 流程执行完成")
        print("=" * 72)
        for k, v in r["result"].items():
            print(f"  {k}: {v}")
    else:
        print(f"\n❌ {r.get('error')}")
        sys.exit(1)

if __name__ == "__main__":
    _cli()