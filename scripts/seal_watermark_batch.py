# scripts/seal_watermark_batch.py
"""
批量给目录下的图片添加印章 + 水印。

用法:
    # 基本用法：处理 output/tang 下所有 PNG，输出到 output/tang_sealed
    python scripts/seal_watermark_batch.py output/tang

    # 指定输出目录
    python scripts/seal_watermark_batch.py output/tang -o output/tang_final

    # 指定印章方案
    python scripts/seal_watermark_batch.py output/tang --scheme contrast

    # 只加水印，不加印章
    python scripts/seal_watermark_batch.py output/tang --no-seal

    # 只加印章，不加水印
    python scripts/seal_watermark_batch.py output/tang --no-watermark

    # 原地覆盖（危险，会覆盖原图！）
    python scripts/seal_watermark_batch.py output/tang --inplace

    # 跳过已有印章的图（按文件名判断，如 xxx_sealed.png）
    python scripts/seal_watermark_batch.py output/tang --skip-sealed

    # 递归子目录
    python scripts/seal_watermark_batch.py output -r
"""
from __future__ import annotations

import argparse
import sys
import shutil
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PIL import Image

# 项目内的印章 / 水印服务
from services.seal_generator import SealGenerator
from services.watermark import WatermarkProcessor
from compose_artwork import ARTIST_NAME


# ============================================================
# 支持的图片格式
# ============================================================
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}


# ============================================================
# 单张处理
# ============================================================
def process_one(
    img_path: Path,
    out_path: Path,
    sg: SealGenerator,
    wp: WatermarkProcessor,
    seal_scheme: str = "contrast",
    add_seal: bool = True,
    add_watermark: bool = True,
    watermark_opacity: int = 30,
    seed: int = None,
) -> bool:
    """
    处理单张图片。

    Returns:
        True 成功 / False 失败
    """
    try:
        img = Image.open(img_path)
        if img.mode != "RGBA":
            img = img.convert("RGBA")

        # ---------- 1. 印章 ----------
        if add_seal:
            try:
                img = sg.apply_scheme(
                    img, ARTIST_NAME,
                    scheme=seal_scheme,
                    margin_ratio=0.05,
                )
            except AttributeError:
                # 兼容旧版 SealGenerator（无 apply_scheme）
                margin = int(min(img.size) * 0.05)
                img = sg.apply(
                    img, ARTIST_NAME,
                    style="bai_wen", shape="square",
                    position="bottom_right",
                    scale=0.14, margin=margin,
                )
                img = sg.apply(
                    img, ARTIST_NAME,
                    style="zhu_wen", shape="rect",
                    position="top_left",
                    scale=0.11, margin=margin,
                )

        # ---------- 2. 水印 ----------
        if add_watermark:
            img = wp.add_subtle_watermark(
                img,
                text=ARTIST_NAME,
                opacity=watermark_opacity,
                font_size=40,
                angle=-30,
                spacing_x=180,
                spacing_y=180,
            )
            if img.mode != "RGBA":
                img = img.convert("RGBA")

        # ---------- 3. 保存 ----------
        out_path.parent.mkdir(parents=True, exist_ok=True)
        img.convert("RGB").save(out_path, quality=95)
        return True

    except Exception as e:
        print(f"   ❌ 失败: {e}")
        return False


# ============================================================
# 主流程
# ============================================================
def main():
    ap = argparse.ArgumentParser(
        description="批量给图片加印章 + 水印",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python scripts/seal_watermark_batch.py output/tang
  python scripts/seal_watermark_batch.py output/tang -o output/tang_final
  python scripts/seal_watermark_batch.py output/tang --scheme classic
  python scripts/seal_watermark_batch.py output/tang --no-watermark
  python scripts/seal_watermark_batch.py output/tang --inplace
        """,
    )

    ap.add_argument("input_dir", help="输入目录")
    ap.add_argument("--output", "-o", default=None,
                    help="输出目录（默认：<input>_sealed）")
    ap.add_argument("--scheme", default="contrast",
                    choices=["classic", "contrast", "luxury", "minimal"],
                    help="印章方案（默认 contrast）")
    ap.add_argument("--no-seal", action="store_true", help="跳过印章")
    ap.add_argument("--no-watermark", action="store_true", help="跳过水印")
    ap.add_argument("--opacity", type=int, default=30,
                    help="水印透明度（0-255，默认 30）")
    ap.add_argument("--seed", type=int, default=None,
                    help="随机种子（水印随机偏移用）")
    ap.add_argument("--inplace", action="store_true",
                    help="原地覆盖（危险！会覆盖原图）")
    ap.add_argument("--recursive", "-r", action="store_true",
                    help="递归子目录")
    ap.add_argument("--skip-sealed", action="store_true",
                    help="跳过文件名含 _sealed 的图")
    ap.add_argument("--extensions", default=".png,.jpg,.jpeg,.webp",
                    help="处理的扩展名（逗号分隔）")

    args = ap.parse_args()

    # ---------- 输入目录 ----------
    input_dir = Path(args.input_dir).resolve()
    if not input_dir.exists() or not input_dir.is_dir():
        print(f"❌ 目录不存在: {input_dir}")
        sys.exit(1)

    # ---------- 输出目录 ----------
    if args.inplace:
        output_dir = input_dir
        print(f"⚠️ 原地模式：会覆盖原图！")
    elif args.output:
        output_dir = Path(args.output).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = input_dir.parent / f"{input_dir.name}_sealed"
        output_dir.mkdir(parents=True, exist_ok=True)

    # ---------- 收集图片 ----------
    exts = {e.strip().lower() for e in args.extensions.split(",") if e.strip()}
    pattern = "**/*" if args.recursive else "*"
    images = [
        p for p in input_dir.glob(pattern)
        if p.is_file() and p.suffix.lower() in exts
    ]
    if args.skip_sealed:
        images = [p for p in images if "_sealed" not in p.stem]
    images = sorted(images)

    if not images:
        print(f"⚠️ 目录下没有找到图片: {input_dir}")
        sys.exit(0)

    # ---------- 初始化服务 ----------
    sg = SealGenerator()
    wp = WatermarkProcessor(seed=args.seed)

    do_seal = not args.no_seal
    do_watermark = not args.no_watermark

    # ---------- 打印配置 ----------
    print("=" * 70)
    print("  批量印章 + 水印")
    print("=" * 70)
    print(f"📂 输入:   {input_dir}")
    print(f"📂 输出:   {output_dir}")
    print(f"🖼️  图片数: {len(images)}")
    print(f"🔖 印章:   {'✅ ' + args.scheme if do_seal else '❌ 跳过'}")
    print(f"💧 水印:   {'✅ opacity=' + str(args.opacity) if do_watermark else '❌ 跳过'}")
    if args.inplace:
        print(f"⚠️ 原地模式: 会覆盖原图")
    print("=" * 70)
    print()

    # ---------- 逐个处理 ----------
    start = datetime.now()
    success = 0
    failed = 0

    for i, img_path in enumerate(images, 1):
        print(f"[{i}/{len(images)}] {img_path.name}")

        # 构造输出路径
        if args.inplace:
            out_path = img_path
        else:
            rel = img_path.relative_to(input_dir)
            out_path = output_dir / rel

        ok = process_one(
            img_path, out_path,
            sg, wp,
            seal_scheme=args.scheme,
            add_seal=do_seal,
            add_watermark=do_watermark,
            watermark_opacity=args.opacity,
            seed=args.seed,
        )

        if ok:
            print(f"   ✅ → {out_path}")
            success += 1
        else:
            failed += 1

    # ---------- 汇总 ----------
    elapsed = (datetime.now() - start).total_seconds()
    print()
    print("=" * 70)
    print(f"  ✅ 完成: {success}/{len(images)} 成功, {failed} 失败")
    print(f"  ⏱️  耗时: {elapsed:.1f} 秒")
    print(f"  📂 输出: {output_dir}")
    print("=" * 70)


if __name__ == "__main__":
    main()