# scripts/ai_mv.py
"""
AI 音乐 MV
ArtForge 出图 → 图片合成视频 → 生成配乐 → 音视频合成 → 推视频号/B站/YouTube

用法：
  python scripts/ai_mv.py --category tang --presets dunhuang feitian --count 3 ^
    --title "敦煌飞天" --duration 40
  python scripts/ai_mv.py --category tang --presets dunhuang --no-publish
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
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


def step_images(category: str, presets: list[str],
                count: int) -> Path:
    """步骤 1：出图"""
    section("步骤 1/5：ArtForge 出图")
    from core.prompt_builder import PromptBuilder
    from api_engines import create_engine
    from compose_artwork import (
        pick_size, theme_from_preset, load_config, ARTIST_NAME)
    from services.aging_processor import AgingProcessor
    from services.inscription_generator import InscriptionGenerator
    from services.seal_generator import SealGenerator
    from compose_artwork import InscriptionRenderer

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = PROJECT_ROOT / "output" / "mv" / f"{ts}_images"
    out_dir.mkdir(parents=True, exist_ok=True)

    builder = PromptBuilder()
    engine = create_engine("pollinations", load_config())

    total = len(presets) * count
    idx = 0
    for preset in presets:
        for i in range(count):
            idx += 1
            print(f"  [{idx}/{total}] {preset} #{i+1}")
            try:
                prompt, detail = builder.compose_preset(
                    preset, category=category, return_detail=True)
                theme = theme_from_preset(preset, category)
                detail.pop("inscription", None)
                full_prompt = ", ".join(
                    detail[k] for k in builder.LAYER_ORDER if detail.get(k))
                negative = builder.get_negative()

                w, h = pick_size(detail)
                img = engine.generate_single(
                    prompt=full_prompt, negative=negative,
                    width=w, height=h)
                if img.mode != "RGBA":
                    img = img.convert("RGBA")

                try:
                    img = AgingProcessor(seed=None).apply(
                        img.convert("RGB"),
                        texture="xuan_paper", strength=0.55,
                    ).convert("RGBA")
                except Exception:
                    pass

                try:
                    ig = InscriptionGenerator(seed=None)
                    text, _ = ig.generate(
                        theme=theme, format="auto", return_meta=True,
                        backend="pollinations", category=category)
                    renderer = InscriptionRenderer()
                    fs = max(24, int(min(w, h) * 0.045))
                    img = renderer.render(
                        img, text, font_size=fs,
                        color=(45, 40, 35),
                        position="top_right",
                        margin=int(min(w, h) * 0.055))
                except Exception:
                    pass

                try:
                    img = SealGenerator().apply_scheme(
                        img, ARTIST_NAME, scheme="contrast",
                        margin_ratio=0.05)
                except Exception:
                    pass

                out = out_dir / f"{preset}_{i+1:02d}.png"
                img.convert("RGB").save(out, quality=95)
            except Exception as e:
                print(f"     ⚠️ {e}")

    print(f"✅ 图片目录: {out_dir}")
    return out_dir


def step_video(image_dir: Path, title: str,
               duration: float) -> Path | None:
    """步骤 2：图片合成视频"""
    section("步骤 2/5：图片合成视频")
    from services.image_to_video import ImageToVideo

    imgs = sorted(p for p in image_dir.iterdir()
                  if p.suffix.lower() in (".png", ".jpg", ".jpeg"))
    if not imgs:
        print("❌ 目录里没有图片")
        return None

    per = max(2.0, duration / len(imgs))
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = "".join(c for c in title[:20]
                   if c.isalnum() or c in " _-").strip() or "mv"
    out = PROJECT_ROOT / "output" / "mv" / f"{ts}_{safe}_video.mp4"

    ImageToVideo().build(
        images=imgs, output=out,
        per_image=per, size="1920x1080", fade=0.6)
    print(f"✅ 视频: {out}")
    return out


def step_music(title: str, duration: float,
               emotion: str = "epic") -> Path | None:
    """步骤 3：生成配乐"""
    section("步骤 3/5：生成配乐")
    try:
        from skills.music_generator.music_generator_cli import MusicGenerator
        gen = MusicGenerator()
        r = gen.create_music(
            topic=title, emotion=emotion,
            duration=int(duration), language="zh")
        if r.get("status") != "success":
            print(f"⚠️ 配乐失败: {r.get('message')}")
            return None
        audio = Path(r["audio_file"])
        print(f"✅ 配乐: {audio}")
        return audio
    except Exception as e:
        print(f"⚠️ 配乐失败: {e}")
        return None


def step_merge(video: Path, audio: Path | None) -> Path:
    """步骤 4：音视频合成"""
    section("步骤 4/5：音视频合成")
    if not audio:
        print("⚠️ 无音频，跳过")
        return video

    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        print("⚠️ 未找到 ffmpeg")
        return video

    out = video.with_name(video.stem + "_final.mp4")
    subprocess.run([
        ffmpeg, "-y",
        "-i", str(video),
        "-stream_loop", "-1", "-i", str(audio),
        "-shortest",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        str(out),
    ], capture_output=True, check=True)
    print(f"✅ {out}")
    return out


def step_publish(video: Path, title: str, desc: str,
                 account: str = "test"):
    """步骤 5：推视频号"""
    section("步骤 5/5：推视频号")
    try:
        from skills.social_auto_upload import SocialAutoUpload
        pub = SocialAutoUpload()
        r = pub.publish_video(
            platform="tencent", file=str(video),
            title=title, desc=desc, tags=[],
            account=account)
        if r.get("status") == "success":
            print("✅ 已推送视频号")
        else:
            print(f"❌ {r.get('error')}")
    except Exception as e:
        print(f"❌ {e}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--category", default="tang")
    ap.add_argument("--presets", nargs="*", default=None)
    ap.add_argument("--count", type=int, default=3)
    ap.add_argument("--title", required=True)
    ap.add_argument("--desc", default="")
    ap.add_argument("--duration", type=float, default=40)
    ap.add_argument("--emotion", default="epic",
                    choices=["peaceful", "melancholic", "joyful",
                             "epic", "mysterious"])
    ap.add_argument("--video-account", default="test")
    ap.add_argument("--no-publish", action="store_true")
    args = ap.parse_args()

    presets = args.presets or ["dunhuang", "feitian"]

    img_dir = step_images(args.category, presets, args.count)
    video = step_video(img_dir, args.title, args.duration)
    if not video:
        sys.exit(1)
    audio = step_music(args.title, args.duration, args.emotion)
    final = step_merge(video, audio)

    if args.no_publish:
        section("步骤 5/5：跳过发布")
        print(f"   视频: {final}")
        return

    step_publish(final, args.title, args.desc or args.title,
                 args.video_account)


if __name__ == "__main__":
    main()