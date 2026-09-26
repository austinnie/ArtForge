# scripts/batch_generate.py
"""批量生成：一次跑多个预设"""
import sys, argparse
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from core.prompt_builder import PromptBuilder
from api_engines import create_engine
from compose_artwork import pick_size, theme_from_preset, load_config


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--category", required=True)
    ap.add_argument("--presets", nargs="+", required=True)
    ap.add_argument("--engine", default="pollinations")
    ap.add_argument("--count", type=int, default=1, help="每个预设生成几张")
    args = ap.parse_args()

    builder = PromptBuilder()
    engine = create_engine(args.engine, load_config())

    for preset in args.presets:
        for i in range(args.count):
            print(f"\n=== {preset} ({i+1}/{args.count}) ===")
            prompt, detail = builder.compose_preset(
                preset, category=args.category, return_detail=True,
            )
            detail.pop("inscription", None)
            parts = [detail[k] for k in builder.LAYER_ORDER if detail.get(k)]
            prompt = ", ".join(parts)
            negative = builder.get_negative()
            w, h = pick_size(detail)
            img = engine.generate_single(
                prompt=prompt, negative=negative, width=w, height=h,
            )
            out_dir = PROJECT_ROOT / "output" / args.category
            out_dir.mkdir(parents=True, exist_ok=True)
            from datetime import datetime
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            out = out_dir / f"{preset}_{ts}.png"
            img.save(out)
            print(f"✅ {out}")


if __name__ == "__main__":
    main()