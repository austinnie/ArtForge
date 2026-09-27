# scripts/ukiyoe_factory.py
"""
浮世绘转换工厂
把原始图片 → 浮世绘 → 印章 → 文章 → 排版 → 推公众号 + 小红书 + 抖音

用法：
  python scripts/ukiyoe_factory.py output/tang
  python scripts/ukiyoe_factory.py output/tang --engine agnes --strength 0.85 ^
    --theme terracotta --footer-image "assets/qr/公众号结束处.png"
  python scripts/ukiyoe_factory.py output/tang --no-publish
  python scripts/ukiyoe_factory.py output/tang --platforms wechat,xiaohongshu
"""
from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from dotenv import load_dotenv
    _env = PROJECT_ROOT / ".env"
    load_dotenv(_env if _env.exists() else None)
except ImportError:
    pass


IMG_EXTS = {".png", ".jpg", ".jpeg", ".webp"}


def section(t: str):
    print()
    print("=" * 72)
    print(f"  {t}")
    print("=" * 72)


def step_convert(input_dir: Path, engine: str, strength: float,
                 seal_text: str) -> Path:
    """步骤 1：批量转浮世绘"""
    section("步骤 1/4：浮世绘转换")
    from skills.ukiyoe_converter import UkiyoeConverter

    out_dir = input_dir.parent / f"{input_dir.name}_ukiyoe"
    out_dir.mkdir(parents=True, exist_ok=True)

    imgs = sorted(p for p in input_dir.iterdir()
                  if p.suffix.lower() in IMG_EXTS)
    if not imgs:
        raise RuntimeError(f"目录里没有图片: {input_dir}")

    conv = UkiyoeConverter()
    ok = 0
    for i, p in enumerate(imgs, 1):
        print(f"  [{i}/{len(imgs)}] {p.name}")
        try:
            r = conv.convert(
                image_path=str(p),
                output_path=str(out_dir / f"{p.stem}_ukiyoe.png"),
                engine_name=engine,
                strength=strength,
                seal_text=seal_text,
            )
            if r.get("status") == "success":
                ok += 1
        except Exception as e:
            print(f"     ⚠️ {e}")
        time.sleep(1.0)

    print(f"\n✅ 转换完成: {ok}/{len(imgs)} → {out_dir}")
    return out_dir


def step_curate(image_dir: Path, title: str) -> Path | None:
    """步骤 2：鉴赏写文章"""
    section("步骤 2/4：鉴赏写文章")
    from skills.image_curator import ImageCurator

    curator = ImageCurator({
        "generate_html": True, "generate_docx": False,
        "generate_pdf": False, "generate_clipboard": True,
    })
    r = curator.curate(str(image_dir), title=title)
    if r.get("status") != "success":
        print(f"❌ 鉴赏失败: {r.get('error')}")
        return None
    md = Path(r["result"]["article_path"])
    print(f"✅ 文章: {md}")
    return md


def step_format(md_path: Path, theme: str,
                footer_image: str | None = None) -> Path | None:
    """步骤 3：微信排版"""
    section("步骤 3/4：微信排版")
    from skills.wechat_formatter import WechatFormatter

    fmt = WechatFormatter()
    kwargs = {"theme": theme, "open": False}
    if footer_image:
        fp = Path(footer_image)
        if not fp.is_absolute():
            fp = PROJECT_ROOT / fp
        if fp.exists():
            kwargs["footer_image"] = str(fp)

    r = fmt.format(str(md_path), **kwargs)
    if r.get("status") != "success":
        print(f"❌ 排版失败: {r.get('error')}")
        return None
    art_dir = Path(r["result"]["article_dir"])
    print(f"✅ 排版: {art_dir}")
    return art_dir


def step_publish(image_dir: Path, article_dir: Path,
                 platforms: list[str], title: str, desc: str):
    """步骤 4：多平台发布"""
    section("步骤 4/4：发布")

    # 公众号
    if "wechat" in platforms:
        print("\n📤 公众号草稿…")
        try:
            from skills.wechat_formatter import WechatFormatter
            r = WechatFormatter().publish(str(article_dir))
            print(f"   {'✅' if r.get('status') == 'success' else '❌'}")
        except Exception as e:
            print(f"   ❌ {e}")

    # 小红书 / 抖音
    for plat in ("xiaohongshu", "douyin"):
        if plat not in platforms:
            continue
        print(f"\n📤 {plat} 图文…")
        try:
            from skills.social_auto_upload import SocialAutoUpload
            pub = SocialAutoUpload()
            imgs = sorted(p for p in image_dir.iterdir()
                          if p.suffix.lower() in IMG_EXTS)[:9]
            r = pub.publish_note(
                platform=plat,
                images=[str(p) for p in imgs],
                title=title[:20],
                note=desc,
                tags=["浮世绘", "东方艺术", "AI绘画"],
                account="test",
            )
            print(f"   {'✅' if r.get('status') == 'success' else '❌'} "
                  f"{r.get('error') or ''}")
        except Exception as e:
            print(f"   ❌ {e}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input_dir", help="原始图片目录")
    ap.add_argument("--engine", default="pollinations",
                    choices=["pollinations", "agnes"])
    ap.add_argument("--strength", type=float, default=0.75)
    ap.add_argument("--seal-text", default="東方藝術")
    ap.add_argument("--theme", default="newspaper")
    ap.add_argument("--title", default=None)
    ap.add_argument("--desc", default="浮世绘风格东方艺术系列")
    ap.add_argument("--footer-image", default=None)
    ap.add_argument("--platforms", default="wechat",
                    help="逗号分隔: wechat,xiaohongshu,douyin")
    ap.add_argument("--no-publish", action="store_true")
    args = ap.parse_args()

    src = Path(args.input_dir)
    if not src.is_absolute():
        src = PROJECT_ROOT / src
    if not src.exists():
        print(f"❌ 目录不存在: {src}")
        sys.exit(1)

    title = args.title or f"浮世绘 · {src.name} {datetime.now():%m-%d}"

    # 1. 转换
    ukiyoe_dir = step_convert(
        src, args.engine, args.strength, args.seal_text)

    # 2. 鉴赏
    md = step_curate(ukiyoe_dir, title)
    if not md:
        sys.exit(1)

    # 3. 排版
    art_dir = step_format(md, args.theme, args.footer_image)
    if not art_dir:
        sys.exit(1)

    # 4. 发布
    if args.no_publish:
        section("步骤 4/4：跳过发布")
        print(f"   图片: {ukiyoe_dir}")
        print(f"   文章: {md}")
        print(f"   排版: {art_dir}")
        return

    platforms = [p.strip() for p in args.platforms.split(",") if p.strip()]
    step_publish(ukiyoe_dir, art_dir, platforms, title, args.desc)


if __name__ == "__main__":
    main()