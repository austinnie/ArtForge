# scripts/novel_daily.py
"""
小说连载号
每章：novel_writer 续写 → ArtForge 出插图 → 排版 → 推公众号

用法：
  # 第 1 次：创建小说
  python scripts/novel_daily.py --title "山海遗事" --genre "奇幻" ^
    --outline "少年在昆仑山下捡到一枚玉佩..." ^
    --characters "主角:林越, 配角:白狐" --chapters 3

  # 续写
  python scripts/novel_daily.py --continue-from output/novels/山海遗事_xxx.txt --chapters 3
"""
from __future__ import annotations

import argparse
import sys
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


def section(t: str):
    print()
    print("=" * 72)
    print(f"  {t}")
    print("=" * 72)


def step_write(title: str, genre: str, outline: str, characters: str,
               chapters: int, continue_from: str | None) -> dict | None:
    """步骤 1：写/续写小说"""
    section("步骤 1/4：写小说")
    from skills.novel_writer.skill import NovelWriterOllama

    writer = NovelWriterOllama()
    kwargs = {
        "genre": genre, "title": title,
        "outline": outline, "characters": characters,
        "chapter_count": chapters,
        "language": "zh",
    }
    if continue_from:
        kwargs["continue_from"] = continue_from

    r = writer.execute(**kwargs)
    if r.get("status") != "success":
        print(f"❌ 写作失败: {r.get('error')}")
        return None
    print(f"✅ 共 {len(r['result']['chapters'])} 章")
    print(f"   保存: {r['result'].get('saved_to')}")
    return r["result"]


def step_illustrate(novel: dict, category: str,
                    per_chapter: int = 1) -> list[Path]:
    """步骤 2：为每章生成插图"""
    section("步骤 2/4：生成章节插图")
    from core.prompt_builder import PromptBuilder
    from api_engines import create_engine
    from compose_artwork import (
        pick_size, load_config, ARTIST_NAME)
    from services.inscription_generator import InscriptionGenerator
    from services.seal_generator import SealGenerator
    from services.aging_processor import AgingProcessor
    from compose_artwork import InscriptionRenderer

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = PROJECT_ROOT / "output" / "novel" / f"{ts}_illustrations"
    out_dir.mkdir(parents=True, exist_ok=True)

    builder = PromptBuilder()
    engine = create_engine("pollinations", load_config())

    imgs: list[Path] = []
    for ch in novel["chapters"]:
        # 用章节标题做插图主题
        theme = ch["title"][:20]
        for k in range(per_chapter):
            print(f"  {ch['title']} — 插图 {k+1}/{per_chapter}")
            prompt, detail = builder.compose_preset(
                "shui_mo", category="gufeng", return_detail=True)
            detail["subject"] = [
                f"illustration for novel chapter: {ch['title']}, "
                f"scene from: {ch['content'][:60]}"
            ]
            detail.pop("inscription", None)
            full_prompt = ", ".join(
                detail[k] for k in builder.LAYER_ORDER if detail.get(k))
            negative = builder.get_negative()

            w, h = pick_size(detail)
            try:
                img = engine.generate_single(
                    prompt=full_prompt, negative=negative,
                    width=w, height=h)
                if img.mode != "RGBA":
                    img = img.convert("RGBA")

                # 做旧
                try:
                    img = AgingProcessor(seed=None).apply(
                        img.convert("RGB"),
                        texture="xuan_paper", strength=0.5,
                    ).convert("RGBA")
                except Exception:
                    pass

                # 题词（用章节标题）
                try:
                    renderer = InscriptionRenderer()
                    fs = max(24, int(min(w, h) * 0.05))
                    img = renderer.render(
                        img, theme,
                        font_size=fs, color=(45, 40, 35),
                        position="top_right",
                        margin=int(min(w, h) * 0.055))
                except Exception:
                    pass

                # 印章
                try:
                    img = SealGenerator().apply_scheme(
                        img, ARTIST_NAME, scheme="contrast",
                        margin_ratio=0.05)
                except Exception:
                    pass

                out = out_dir / f"ch{ch['index']:02d}_{k+1}.png"
                img.convert("RGB").save(out, quality=95)
                imgs.append(out)
            except Exception as e:
                print(f"     ⚠️ {e}")

    print(f"\n✅ 共 {len(imgs)} 张插图 → {out_dir}")
    return imgs


def step_compose_md(novel: dict, images: list[Path]) -> Path:
    """步骤 3：把小说 + 插图拼成 Markdown"""
    section("步骤 3/4：拼装 Markdown")
    md_path = Path(novel.get("saved_to", "")).with_suffix(".md")
    if not md_path.parent.exists():
        md_path = PROJECT_ROOT / "output" / "novel" / md_path.name

    lines = [f"# {novel['title']}", "",
             f"> {novel.get('genre', '')} · "
             f"{datetime.now():%Y-%m-%d}", "",
             novel.get("summary", ""), "", "---", ""]

    for i, ch in enumerate(novel["chapters"]):
        lines.append(f"## 第 {ch['index']} 章 · {ch['title']}")
        lines.append("")
        # 章节插图
        ch_imgs = [p for p in images
                   if p.name.startswith(f"ch{ch['index']:02d}_")]
        if ch_imgs:
            for img in ch_imgs:
                lines.append(f"![{ch['title']}]({img.as_posix()})")
                lines.append("")
        lines.append(ch["content"])
        lines.append("")
        lines.append("---")
        lines.append("")

    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ {md_path}")
    return md_path


def step_format_and_publish(md_path: Path, theme: str,
                            publish: bool):
    section("步骤 4/4：排版" + (" + 推送" if publish else ""))
    from skills.wechat_formatter import WechatFormatter
    fmt = WechatFormatter()
    r = fmt.format(str(md_path), theme=theme, open=False)
    if r.get("status") != "success":
        print(f"❌ 排版失败: {r.get('error')}")
        return
    art_dir = Path(r["result"]["article_dir"])
    print(f"✅ 排版: {art_dir}")

    if publish:
        p = fmt.publish(str(art_dir))
        if p.get("status") == "success":
            print("✅ 已推送公众号草稿")
        else:
            print(f"❌ 推送失败: {p.get('error')}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", default="山海遗事")
    ap.add_argument("--genre", default="奇幻")
    ap.add_argument("--outline", default="少年在昆仑山下捡到一枚玉佩")
    ap.add_argument("--characters", default="主角:林越, 配角:白狐")
    ap.add_argument("--chapters", type=int, default=3)
    ap.add_argument("--continue-from", default=None,
                    help="续写：给上次的小说 txt 路径")
    ap.add_argument("--theme", default="ink")
    ap.add_argument("--publish", action="store_true")
    args = ap.parse_args()

    # 1. 写
    novel = step_write(
        args.title, args.genre, args.outline,
        args.characters, args.chapters, args.continue_from)
    if not novel:
        sys.exit(1)

    # 2. 插图
    images = step_illustrate(novel, "gufeng")

    # 3. 拼 md
    md = step_compose_md(novel, images)

    # 4. 排版 + 推送
    step_format_and_publish(md, args.theme, args.publish)


if __name__ == "__main__":
    main()