# skills/artforge_daily/skill.py
"""
ArtForge 日更号 —— 走 6 层预设的完整流水线

流程：
  1. 用 ArtForge 6 层预设出图
  2. 做旧 → 题词 → 印章 → 装裱 → 水印
  3. image_curator 鉴赏写文章
  4. wechat_formatter 排版
  5. 推公众号草稿（图文）
  6. 推公众号贴图（图片消息）
  7. 图片合成视频，推视频号

用法：
  from skills.artforge_daily import ArtForgeDaily
  pipe = ArtForgeDaily()
  pipe.execute(category="tang", presets=["dunhuang","feitian"], count=3)

  # CLI
  python -m skills.artforge_daily.skill --category tang --presets dunhuang feitian --count 3
"""
from __future__ import annotations

import argparse
import logging
import sys
import time
import traceback
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
# 自动发现预设（不再写死 DEFAULT_PRESETS）
# ============================================================

PRESETS_DIR = PROJECT_ROOT / "presets"


def list_categories() -> List[str]:
    """扫描 presets/ 下所有含 .py 的分类"""
    if not PRESETS_DIR.exists():
        return []
    cats = []
    for d in sorted(PRESETS_DIR.iterdir()):
        if not d.is_dir() or d.name.startswith("."):
            continue
        py_files = [f for f in d.glob("*.py")
                    if f.stem not in ("__init__", "__pycache__")]
        if py_files:
            cats.append(d.name)
    return cats


def list_presets(category: str) -> List[str]:
    """列出某分类下的所有预设名"""
    d = PRESETS_DIR / category
    if not d.exists():
        return []
    return sorted(
        f.stem for f in d.glob("*.py")
        if f.stem not in ("__init__",)
    )


def pick_default_presets(category: str, count: int = 3) -> List[str]:
    """
    用户没指定 presets 时，从分类下随机挑 count 个
    """
    import random
    all_presets = list_presets(category)
    if not all_presets:
        return []
    if len(all_presets) <= count:
        return all_presets
    return random.sample(all_presets, count)


class ArtForgeDaily:
    name = "artforge_daily"
    version = "1.0.0"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self._setup_logging()

    def _setup_logging(self):
        level = self.config.get("log_level", "INFO")
        logging.basicConfig(
            level=getattr(logging, level.upper()),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    # ---------- 步骤 1：生成图片 ----------

    def generate_images(
        self,
        category: str,
        presets: List[str],
        count: int,
        engine: str,
        composition: str,
        seed: Optional[int],
        seal_scheme: str,
        language: str,
        use_aging: bool = True,
        use_inscription: bool = True,
        use_seal: bool = True,
        use_scroll: bool = True,
        use_watermark: bool = True,
    ) -> Path:
        from core.prompt_builder import PromptBuilder
        from core.safety import check_safety
        from api_engines import create_engine
        from compose_artwork import (
            InscriptionRenderer, pick_size, theme_from_preset,
            load_config, ARTIST_NAME,
        )

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir = PROJECT_ROOT / "output" / "daily" / f"{ts}_images"
        out_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"输出目录: {out_dir}")

        builder = PromptBuilder()
        engine_obj = create_engine(engine, load_config())

        comp_map = {
            "vertical":   "vertical hanging scroll, kakemono",
            "horizontal": "horizontal handscroll, emaki",
            "byobu":      "folding screen, byobu, multi-panel",
            "fan":        "round fan, circular composition",
            "album":      "square album leaf",
        }

        total = len(presets) * count
        idx = 0
        produced: List[Path] = []
        failed: List[str] = []

        for preset in presets:
            for i in range(count):
                idx += 1
                tag = f"{preset}_{i+1:02d}"
                logger.info(f"[{idx}/{total}] 生成 {tag}")

                try:
                    prompt, detail = builder.compose_preset(
                        preset, category=category, return_detail=True)
                    theme = theme_from_preset(preset, category)
                    detail["composition"] = comp_map.get(
                        composition, comp_map["vertical"])
                    detail.pop("inscription", None)
                    full_prompt = ", ".join(
                        detail[k] for k in builder.LAYER_ORDER if detail.get(k))

                    negative = builder.get_negative() + (
                        ", calligraphy, text, chinese characters, japanese text, "
                        "kanji, kana, seal, stamp, signature, inscription, "
                        "poem text, red seal, watermark, logo, letters, words")

                    is_safe, reason = check_safety(
                        full_prompt, detail.get("style", ""),
                        detail.get("subject", ""))
                    if not is_safe:
                        logger.warning(f"{tag} 安全检查未过: {reason}")
                        failed.append(tag)
                        continue

                    width, height = pick_size(detail)
                    image = engine_obj.generate_single(
                        prompt=full_prompt, negative=negative,
                        width=width, height=height, seed=seed)
                    if image.mode != "RGBA":
                        image = image.convert("RGBA")

                    # 做旧
                    if use_aging:
                        try:
                            from services.aging_processor import AgingProcessor
                            image = AgingProcessor(seed=seed).apply(
                                image.convert("RGB"),
                                texture="xuan_paper", strength=0.55,
                            ).convert("RGBA")
                        except Exception as e:
                            logger.warning(f"做旧失败: {e}")

                    # 题词
                    if use_inscription:
                        try:
                            from services.inscription_generator import (
                                InscriptionGenerator)
                            ig = InscriptionGenerator(seed=seed)
                            lang = None if language == "auto" else language
                            inscription_text, _ = ig.generate(
                                theme=theme, format="auto", return_meta=True,
                                backend=engine if engine in
                                ("agnes", "pollinations") else "auto",
                                category=category, language=lang)
                            renderer = InscriptionRenderer()
                            fs = max(24, int(min(width, height) * 0.045))
                            image = renderer.render(
                                image, inscription_text, font_size=fs,
                                color=(45, 40, 35),
                                position="top_right",
                                margin=int(min(width, height) * 0.055),
                                max_chars_per_col=8)
                        except Exception as e:
                            logger.warning(f"题词失败: {e}")

                    # 印章
                    if use_seal:
                        try:
                            from services.seal_generator import SealGenerator
                            image = SealGenerator().apply_scheme(
                                image, ARTIST_NAME,
                                scheme=seal_scheme, margin_ratio=0.05)
                        except Exception as e:
                            logger.warning(f"印章失败: {e}")

                    # 装裱
                    if use_scroll:
                        try:
                            from services.scroll_composer import ScrollComposer
                            image = ScrollComposer(seed=seed).compose(
                                image.convert("RGB"),
                                composition=composition).convert("RGBA")
                        except Exception as e:
                            logger.warning(f"装裱失败: {e}")

                    # 水印
                    if use_watermark:
                        try:
                            from services.watermark import WatermarkProcessor
                            image = WatermarkProcessor(seed=seed) \
                                .add_subtle_watermark(
                                    image, text=ARTIST_NAME,
                                    opacity=30, font_size=40,
                                    angle=-30,
                                    spacing_x=180, spacing_y=180)
                            if image.mode != "RGBA":
                                image = image.convert("RGBA")
                        except Exception as e:
                            logger.warning(f"水印失败: {e}")

                    out_path = out_dir / f"{preset}_{i+1:02d}.png"
                    image.convert("RGB").save(out_path, quality=95)
                    produced.append(out_path)
                    logger.info(f"  → {out_path.name}")

                    if idx < total:
                        time.sleep(1.5)

                except Exception as e:
                    logger.error(f"{tag} 失败: {e}")
                    traceback.print_exc()
                    failed.append(tag)

        logger.info(f"生成完成: {len(produced)} 成功 / {len(failed)} 失败")
        return out_dir

    # ---------- 步骤 2：鉴赏 ----------

    def curate(self, image_dir: Path, title: Optional[str] = None) -> Optional[Path]:
        from skills.image_curator import ImageCurator

        if not title:
            title = f"东方艺术 · {datetime.now().strftime('%Y-%m-%d')}"

        curator = ImageCurator({
            "generate_html": True,
            "generate_docx": False,
            "generate_pdf": False,
            "generate_clipboard": True,
        })
        r = curator.curate(str(image_dir), title=title)
        if r.get("status") != "success":
            logger.error(f"鉴赏失败: {r.get('error')}")
            return None
        return Path(r["result"]["article_path"])

    # ---------- 步骤 3：排版 ----------

    def format(self, md_path: Path, theme: str,
               footer_image: Optional[str] = None) -> Optional[Path]:
        from skills.wechat_formatter import WechatFormatter

        fmt = WechatFormatter()
        kwargs = {"theme": theme, "open": False}
        if footer_image:
            fp = Path(footer_image)
            if not fp.is_absolute():
                fp = PROJECT_ROOT / fp
            if fp.exists():
                kwargs["footer_image"] = str(fp)
                kwargs["footer_alt"] = "关注"

        r = fmt.format(str(md_path), **kwargs)
        if r.get("status") != "success":
            logger.error(f"排版失败: {r.get('error')}")
            return None
        return Path(r["result"]["article_dir"])

    # ---------- 步骤 4：推文章草稿 ----------

    def push_article(self, article_dir: Path, dry_run: bool = False) -> Dict:
        from skills.wechat_formatter import WechatFormatter
        fmt = WechatFormatter()
        r = fmt.publish(str(article_dir), dry_run=dry_run)
        return {"ok": r.get("status") == "success", "error": r.get("error")}

    # ---------- 步骤 5：推贴图 ----------

    def push_newspic(self, image_dir: Path, title: str,
                     content: str = "") -> Dict:
        try:
            from skills.wechat_formatter.publisher import wechat_publish as wp

            imgs = sorted([
                p for p in image_dir.iterdir()
                if p.suffix.lower() in (".png", ".jpg", ".jpeg")
            ])[:20]
            if not imgs:
                return {"ok": False, "error": "目录里没有图片"}

            token = wp.get_access_token()
            media_ids = wp.upload_images_as_material(
                token, [str(p) for p in imgs])
            if not media_ids:
                return {"ok": False, "error": "所有图片上传失败"}

            media_id = wp.push_draft(
                token, title=title[:20],
                content=content[:1000] or title[:20],
                article_type="newspic",
                image_media_ids=media_ids)
            return {"ok": bool(media_id), "media_id": media_id}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ---------- 步骤 6：合成视频 + 推视频号 ----------

    def build_video(self, image_dir: Path, title: str,
                    per_image: float = 4.0,
                    size: str = "1080x1920",
                    bgm: Optional[Path] = None) -> Optional[Path]:
        import shutil
        import subprocess

        ffmpeg = shutil.which("ffmpeg")
        if not ffmpeg:
            logger.error("未找到 ffmpeg")
            return None

        imgs = sorted([
            p for p in image_dir.iterdir()
            if p.suffix.lower() in (".png", ".jpg", ".jpeg")
        ])
        if not imgs:
            return None

        W, H = map(int, size.split("x"))
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe = "".join(c for c in title[:20]
                       if c.isalnum() or c in " _-").strip() or "video"
        out = PROJECT_ROOT / "output" / "videos" / f"{ts}_{safe}.mp4"
        out.parent.mkdir(parents=True, exist_ok=True)

        import tempfile
        work = Path(tempfile.mkdtemp(prefix="af_video_"))
        try:
            segs = []
            for i, img in enumerate(imgs):
                seg = work / f"seg_{i:03d}.mp4"
                vf = (
                    f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
                    f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black,"
                    f"setsar=1,format=yuv420p")
                subprocess.run([
                    ffmpeg, "-y", "-loop", "1",
                    "-t", str(per_image), "-i", str(img),
                    "-vf", vf, "-r", "30",
                    "-c:v", "libx264", "-preset", "medium",
                    "-crf", "20", "-pix_fmt", "yuv420p", str(seg),
                ], capture_output=True, check=True)
                segs.append(seg)

            concat = work / "concat.txt"
            concat.write_text(
                "\n".join(f"file '{s.as_posix()}'" for s in segs),
                encoding="utf-8")
            merged = work / "merged.mp4"
            subprocess.run([
                ffmpeg, "-y", "-f", "concat", "-safe", "0",
                "-i", str(concat), "-c", "copy", str(merged),
            ], capture_output=True, check=True)

            if bgm and bgm.exists():
                subprocess.run([
                    ffmpeg, "-y", "-i", str(merged),
                    "-stream_loop", "-1", "-i", str(bgm),
                    "-shortest", "-c:v", "copy", "-c:a", "aac",
                    "-b:a", "128k", str(out),
                ], capture_output=True, check=True)
            else:
                shutil.copy2(merged, out)
            return out
        finally:
            shutil.rmtree(work, ignore_errors=True)

    def push_video(self, video_path: Path, title: str, desc: str = "",
                   cover: Optional[Path] = None,
                   account: str = "test") -> Dict:
        try:
            from skills.social_auto_upload import SocialAutoUpload
            pub = SocialAutoUpload()
            r = pub.publish_video(
                platform="tencent", file=str(video_path),
                title=title, desc=desc, tags=[],
                account=account,
                thumbnail=str(cover) if cover and cover.exists() else None)
            return {"ok": r.get("status") == "success",
                    "error": r.get("error")}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ---------- 主流程 ----------

    def execute(self, **kwargs) -> Dict[str, Any]:
        start = time.time()
        logger.info(f"执行 {self.name} v{self.version}")

        import random

        category = kwargs.get("category")
        presets = kwargs.get("presets")

        # 1) 分类没给 → 从全部分类里随机挑一个
        if not category:
            all_cats = list_categories()
            if not all_cats:
                return {"status": "error",
                        "error": "presets/ 下没有任何分类"}
            category = random.choice(all_cats)
            logger.info(f"未指定分类，随机选中: {category}")

        # 2) 预设没给 → 从该分类下随机挑 3 个
        if not presets:
            presets = pick_default_presets(category, count=3)
            if not presets:
                all_cats = list_categories()
                return {
                    "status": "error",
                    "error": f"分类 {category} 下没有预设。"
                             f"可用分类: {all_cats}",
                }
            logger.info(f"未指定预设，随机选中: {presets}")

        count = int(kwargs.get("count", 2))
        engine = kwargs.get("engine", "pollinations")
        composition = kwargs.get("composition", "vertical")
        theme = kwargs.get("theme", "newspaper")
        seed = kwargs.get("seed")
        seal_scheme = kwargs.get("seal_scheme", "contrast")
        language = kwargs.get("language", "auto")

        push_article = kwargs.get("push_article", True)
        push_newspic_flag = kwargs.get("push_newspic", True)
        push_video_flag = kwargs.get("push_video", True)
        dry_run = kwargs.get("dry_run", False)
        footer_image = kwargs.get("footer_image")
        bgm = kwargs.get("bgm")
        video_account = kwargs.get("video_account", "test")
        title = kwargs.get("title")

        result: Dict[str, Any] = {
            "image_dir": None, "md_path": None, "article_dir": None,
            "video_path": None,
            "push_article": None, "push_newspic": None, "push_video": None,
        }

        try:
            # 1. 生成
            image_dir = self.generate_images(
                category=category, presets=presets, count=count,
                engine=engine, composition=composition, seed=seed,
                seal_scheme=seal_scheme, language=language,
            )
            result["image_dir"] = str(image_dir)
            if not list(image_dir.glob("*.png")):
                return {"status": "error", "error": "没有生成任何图片"}

            # 2. 鉴赏
            md = self.curate(image_dir, title=title)
            if not md:
                return {"status": "error", "error": "鉴赏失败",
                        "result": result}
            result["md_path"] = str(md)

            # 3. 排版
            art_dir = self.format(md, theme, footer_image=footer_image)
            if not art_dir:
                return {"status": "error", "error": "排版失败",
                        "result": result}
            result["article_dir"] = str(art_dir)

            # 4. 推文章
            if push_article:
                result["push_article"] = self.push_article(art_dir, dry_run)

            # 5. 推贴图
            if push_newspic_flag:
                np_title = (title or f"{category} · "
                            f"{datetime.now().strftime('%m-%d')}")[:20]
                result["push_newspic"] = self.push_newspic(
                    image_dir, np_title)

            # 6. 视频
            if push_video_flag:
                v_title = (title or f"东方艺术 · {category}")[:20]
                bgm_path = Path(bgm) if bgm else None
                if bgm_path and not bgm_path.is_absolute():
                    bgm_path = PROJECT_ROOT / bgm_path
                video = self.build_video(
                    image_dir, v_title, bgm=bgm_path)
                if video:
                    result["video_path"] = str(video)
                    cover = next(image_dir.glob("*.png"), None)
                    result["push_video"] = self.push_video(
                        video, v_title, desc=v_title,
                        cover=cover, account=video_account)

            return {
                "status": "success",
                "result": result,
                "metadata": {
                    "skill": self.name, "version": self.version,
                    "elapsed": f"{time.time() - start:.1f}s",
                },
            }
        except Exception as e:
            logger.error(f"执行失败: {e}")
            traceback.print_exc()
            return {"status": "error", "error": str(e), "result": result}


# ============================================================
# CLI
# ============================================================

# ============================================================
# CLI
# ============================================================

def _cli():
    ap = argparse.ArgumentParser(
        description="ArtForge 日更号（预设 → 图 → 文章 → 草稿 → 贴图 → 视频号）")
    ap.add_argument("--category", default=None,
                    help="分类，不指定则随机")
    ap.add_argument("--presets", nargs="*", default=None,
                    help="预设名，不指定则从分类下随机挑 3 个")
    ap.add_argument("--list-categories", action="store_true",
                    help="列出所有分类后退出")
    ap.add_argument("--list-presets", metavar="CATEGORY", default=None,
                    help="列出某分类下的所有预设后退出")
    ap.add_argument("--count", type=int, default=2)
    ap.add_argument("--engine", default="pollinations",
                    choices=["pollinations", "agnes", "siliconflow"])
    ap.add_argument("--composition", default="vertical",
                    choices=["vertical", "horizontal", "byobu", "fan", "album"])
    ap.add_argument("--theme", default="newspaper")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--seal-scheme", default="contrast")
    ap.add_argument("--language", default="auto")

    ap.add_argument("--no-article", action="store_true")
    ap.add_argument("--no-newspic", action="store_true")
    ap.add_argument("--no-video", action="store_true")

    ap.add_argument("--footer-image", default=None)
    ap.add_argument("--bgm", default=None)
    ap.add_argument("--video-account", default="test")
    ap.add_argument("--title", default=None)
    ap.add_argument("--dry-run", action="store_true")

    args = ap.parse_args()

    # ---- 辅助命令：列出分类 ----
    if args.list_categories:
        cats = list_categories()
        if not cats:
            print("presets/ 下没有任何分类")
            return
        print(f"\n共 {len(cats)} 个分类:")
        for c in cats:
            n = len(list_presets(c))
            print(f"  {c:22s} ({n} 个预设)")
        return

    # ---- 辅助命令：列出某分类下的预设 ----
    if args.list_presets:
        presets = list_presets(args.list_presets)
        if not presets:
            print(f"分类 {args.list_presets} 不存在或为空")
            return
        print(f"\n{args.list_presets} 下的 {len(presets)} 个预设:")
        for p in presets:
            print(f"  {p}")
        return

    # ---- 正常流程 ----
    pipe = ArtForgeDaily()
    r = pipe.execute(
        category=args.category, presets=args.presets, count=args.count,
        engine=args.engine, composition=args.composition, theme=args.theme,
        seed=args.seed, seal_scheme=args.seal_scheme, language=args.language,
        push_article=not args.no_article,
        push_newspic=not args.no_newspic,
        push_video=not args.no_video,
        footer_image=args.footer_image, bgm=args.bgm,
        video_account=args.video_account, title=args.title,
        dry_run=args.dry_run,
    )
    if r["status"] == "success":
        print("\n" + "=" * 72)
        print("  ✅ ArtForge 日更完成")
        print("=" * 72)
        for k, v in r["result"].items():
            print(f"  {k}: {v}")
    else:
        print(f"\n❌ {r.get('error')}")
        sys.exit(1)


if __name__ == "__main__":
    _cli()