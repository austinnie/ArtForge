# test_pipeline.py
"""
ArtForge 最小链路验证：tengu 预设 → prompt → 出图 → 保存

先用 Pollinations（无需 API Key），一次跑通。
用法:
    python test_pipeline.py
    python test_pipeline.py --engine agnes
    python test_pipeline.py --engine pollinations --preset tengu --seed 42
"""

import argparse
import os
import sys
from pathlib import Path
from datetime import datetime

# 让 python test_pipeline.py 能直接 import 项目内模块
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.prompt_builder import PromptBuilder


# 画幅 → 宽高（对齐 PROGRESS.md 的约定）
COMPOSITION_SIZE = {
    "vertical":   (768, 1365),   # 立轴 9:16
    "horizontal": (1365, 768),   # 横卷 16:9
    "byobu":      (1024, 768),   # 屏风 4:3
    "fan":        (1024, 1024),  # 团扇 1:1
    "album":      (768, 1024),   # 册页 3:4
}


def load_config() -> dict:
    """从 .env / 环境变量读 API Key。没装 dotenv 也不报错。"""
    try:
        from dotenv import load_dotenv
        load_dotenv(PROJECT_ROOT / ".env")
    except ImportError:
        pass

    return {
        "POLLINATIONS_API_KEY": os.getenv("POLLINATIONS_API_KEY"),
        "POLLINATIONS_MODEL": os.getenv("POLLINATIONS_MODEL"),
        "AGNES_API_KEY": os.getenv("AGNES_API_KEY"),
        "AGNES_BASE_URL": os.getenv("AGNES_BASE_URL"),
        "AGNES_IMAGE_MODEL": os.getenv("AGNES_IMAGE_MODEL"),
        "SILICONFLOW_API_KEY": os.getenv("SILICONFLOW_API_KEY"),
        "SILICONFLOW_MODEL": os.getenv("SILICONFLOW_MODEL"),
    }


def build_prompt(preset: str, category: str, detail_out: bool = True):
    """用预设组合 prompt。返回 (prompt, detail, negative)。"""
    builder = PromptBuilder()
    prompt, detail = builder.compose_preset(
        preset, category=category, return_detail=True,
    )
    negative = builder.get_negative()
    return prompt, detail, negative


def pick_size(detail: dict):
    """根据 composition 层猜画幅尺寸。"""
    comp = (detail.get("composition") or "").lower()
    for key, size in COMPOSITION_SIZE.items():
        if key in comp:
            return size
    # 关键词兜底
    if any(w in comp for w in ["vertical", "scroll", "hanging", "立轴", "挂轴"]):
        return COMPOSITION_SIZE["vertical"]
    if any(w in comp for w in ["horizontal", "handscroll", "横卷", "长卷"]):
        return COMPOSITION_SIZE["horizontal"]
    if any(w in comp for w in ["fan", "团扇", "round"]):
        return COMPOSITION_SIZE["fan"]
    if any(w in comp for w in ["screen", "byobu", "屏风"]):
        return COMPOSITION_SIZE["byobu"]
    return COMPOSITION_SIZE["vertical"]  # 默认立轴


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", default="pollinations",
                    choices=["pollinations", "agnes", "siliconflow"])
    ap.add_argument("--preset", default="tengu")
    ap.add_argument("--category", default="yokai")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--out", default=None, help="输出文件路径")
    args = ap.parse_args()

    print("=" * 70)
    print("  ArtForge 链路验证")
    print("=" * 70)

    # 1. 组 prompt
    print(f"\n📚 加载预设: {args.category}/{args.preset}")
    prompt, detail, negative = build_prompt(args.preset, args.category)

    print("\n📋 各层明细:")
    for k, v in detail.items():
        print(f"  [{k:12s}] {v}")

    print(f"\n📝 Prompt:\n{prompt}")
    print(f"\n🚫 Negative:\n{negative}")

    # 2. 尺寸
    width, height = pick_size(detail)
    print(f"\n🖼️  画幅: {width}x{height}")

    # 3. 建引擎
    from api_engines import create_engine
    config = load_config()

    print(f"\n🔌 创建引擎: {args.engine}")
    engine = create_engine(args.engine, config)

    # 4. 出图
    print(f"\n🎨 开始生成（可能需要 10-60 秒）...")
    image = engine.generate_single(
        prompt=prompt,
        negative=negative,
        width=width,
        height=height,
        seed=args.seed,
    )

    # 5. 保存
    out_dir = PROJECT_ROOT / "output" / args.category
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.out:
        out_path = Path(args.out)
    else:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = out_dir / f"{args.preset}_{ts}.png"

    image.save(out_path)
    print(f"\n✅ 已保存: {out_path}")
    print(f"   尺寸: {image.size[0]}x{image.size[1]}")

    print("\n" + "=" * 70)
    print("  ✅ 链路跑通")
    print("=" * 70)


if __name__ == "__main__":
    main()