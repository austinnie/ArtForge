# compose_artwork.py
"""
ArtForge 全流程合成 — 一条龙出一张带题词/印章/做旧的完整作品

流程:
    1. PromptBuilder   → 从预设组合 prompt（默认剔除 inscription 层）
    2. API 引擎        → 出图
    3. AgingProcessor  → 做旧（宣纸纹理 + 老化）
    4. InscriptionRenderer → 题词竖排渲染到画面（带底衬）
    5. SealGenerator   → 钤印（右下 + 左上）
    6. 保存成品 + 元信息

设计决策:
    - 默认 --clean-prompt: 从 prompt 移除 inscription 层，
      让 AI 只画画，题词印章全交 PIL 合成（可控、可复现、可改字）

用法:
    python compose_artwork.py
    python compose_artwork.py --preset tengu --engine pollinations
    python compose_artwork.py --preset kappa --format haiku --seed 42
    python compose_artwork.py --no-aging --no-inscription --no-seal
    python compose_artwork.py --no-clean-prompt   # 让 AI 自己画题词印章
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

from PIL import Image, ImageDraw, ImageFont


# ============================================================
# 路径修正 + .env
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent
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


# ============================================================
# 画幅 → 尺寸
# ============================================================

COMPOSITION_SIZE = {
    "vertical":   (768, 1365),
    "horizontal": (1365, 768),
    "byobu":      (1024, 768),
    "fan":        (1024, 1024),
    "album":      (768, 1024),
}


# ============================================================
# 题词渲染器（竖排，从右往左，带底衬）
# ============================================================

class InscriptionRenderer:
    """把题词文本竖排渲染到画面上"""

    FONT_CANDIDATES = [
        PROJECT_ROOT / "assets" / "fonts" / "calligraphy.ttf",
        PROJECT_ROOT / "assets" / "fonts" / "kai.ttf",
        Path("C:/Windows/Fonts/simkai.ttf"),
        Path("C:/Windows/Fonts/simsun.ttc"),
        Path("C:/Windows/Fonts/msyh.ttc"),
        Path("/System/Library/Fonts/PingFang.ttc"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]

    def __init__(self, font_path: Optional[Path] = None):
        self.font_path = self._resolve_font(font_path)

    def _resolve_font(self, font_path) -> Optional[Path]:
        if font_path and Path(font_path).exists():
            return Path(font_path)
        for p in self.FONT_CANDIDATES:
            if p.exists():
                return p
        return None

    def _load_font(self, size: int) -> ImageFont.FreeTypeFont:
        if self.font_path:
            try:
                return ImageFont.truetype(str(self.font_path), size)
            except Exception:
                pass
        return ImageFont.load_default()

    def render(
        self,
        canvas: Image.Image,
        text: str,
        font_size: int = 36,
        color: Tuple[int, int, int] = (40, 35, 30),
        position: str = "top_right",
        margin: int = 50,
        line_gap_ratio: float = 0.15,
        max_chars_per_col: int = 8,
        bg_alpha: int = 180,
        bg_color: Tuple[int, int, int] = (250, 248, 240),
    ) -> Image.Image:
        """
        把题词竖排渲染到画面上（从右往左）。

        Args:
            canvas:            画布（RGBA）
            text:              题词文本（可含换行）
            font_size:         字号
            color:             墨色
            position:          top_right / top_left / bottom_right / bottom_left
            margin:            边距
            line_gap_ratio:    列间距（相对字号）
            max_chars_per_col: 每列最多几字，超出换列
            bg_alpha:          底衬透明度 0-255（0 表示不加底衬）
            bg_color:          底衬颜色（默认宣纸米白）

        Returns:
            合成后的 RGBA 图像
        """
        if not text.strip():
            return canvas

        if canvas.mode != "RGBA":
            canvas = canvas.convert("RGBA")

        # 1. 拆列
        raw_lines = [l for l in text.split("\n") if l.strip()]
        columns = []
        for line in raw_lines:
            line = line.strip()
            if not line:
                continue
            for i in range(0, len(line), max_chars_per_col):
                columns.append(line[i:i + max_chars_per_col])

        if not columns:
            return canvas

        # 2. 量尺寸
        font = self._load_font(font_size)
        draw = ImageDraw.Draw(canvas)

        bbox = draw.textbbox((0, 0), "国", font=font)
        char_w = bbox[2] - bbox[0]
        char_h = bbox[3] - bbox[1]

        col_gap = int(font_size * (1.0 + line_gap_ratio))
        char_gap = int(font_size * 0.15)

        n_cols = len(columns)
        max_col_len = max(len(c) for c in columns)

        block_w = n_cols * col_gap - (col_gap - char_w)
        block_h = max_col_len * (char_h + char_gap) - char_gap

        cw, ch = canvas.size

        # 3. 起始位置
        if "right" in position:
            x_start = cw - margin - block_w
        else:
            x_start = margin

        if "top" in position:
            y_start = margin
        else:
            y_start = ch - margin - block_h

        # ---------- 3.5 底衬（半透明白） ----------
        if bg_alpha > 0:
            pad = int(font_size * 0.45)
            bg_x0 = max(0, x_start - pad)
            bg_y0 = max(0, y_start - pad)
            bg_x1 = min(cw, x_start + block_w + pad)
            bg_y1 = min(ch, y_start + block_h + pad)

            overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
            od = ImageDraw.Draw(overlay)
            od.rectangle(
                [bg_x0, bg_y0, bg_x1, bg_y1],
                fill=bg_color + (bg_alpha,),
            )
            canvas = Image.alpha_composite(canvas, overlay)
            draw = ImageDraw.Draw(canvas)   # 重取 draw

        # 4. 逐列逐字绘制（从右往左）
        for ci, col in enumerate(columns):
            x = x_start + (n_cols - 1 - ci) * col_gap
            y = y_start
            for ch_char in col:
                bbox = draw.textbbox((0, 0), ch_char, font=font)
                ox, oy = bbox[0], bbox[1]
                draw.text(
                    (x - ox, y - oy),
                    ch_char,
                    font=font,
                    fill=color + (255,) if len(color) == 3 else color,
                )
                y += char_h + char_gap

        return canvas


# ============================================================
# 配置 / 工具
# ============================================================

def load_config() -> Dict[str, str]:
    """读 .env → config dict（传给 create_engine）"""
    return {
        "POLLINATIONS_API_KEY": os.getenv("POLLINATIONS_API_KEY"),
        "POLLINATIONS_MODEL": os.getenv("POLLINATIONS_MODEL"),
        "AGNES_API_KEY": os.getenv("AGNES_API_KEY"),
        "AGNES_BASE_URL": os.getenv("AGNES_BASE_URL"),
        "AGNES_IMAGE_MODEL": os.getenv("AGNES_IMAGE_MODEL"),
        "SILICONFLOW_API_KEY": os.getenv("SILICONFLOW_API_KEY"),
        "SILICONFLOW_MODEL": os.getenv("SILICONFLOW_MODEL"),
    }


def pick_size(detail: Dict[str, str]) -> Tuple[int, int]:
    """根据 composition 层猜画幅尺寸"""
    comp = (detail.get("composition") or "").lower()
    if any(w in comp for w in ["vertical", "scroll", "hanging", "立轴", "挂轴"]):
        return COMPOSITION_SIZE["vertical"]
    if any(w in comp for w in ["horizontal", "handscroll", "横卷", "长卷"]):
        return COMPOSITION_SIZE["horizontal"]
    if any(w in comp for w in ["fan", "团扇", "round"]):
        return COMPOSITION_SIZE["fan"]
    if any(w in comp for w in ["screen", "byobu", "屏风"]):
        return COMPOSITION_SIZE["byobu"]
    if any(w in comp for w in ["album", "册页"]):
        return COMPOSITION_SIZE["album"]
    return COMPOSITION_SIZE["vertical"]


def theme_from_preset(preset: str, category: str) -> str:
    """从预设名推主题，用于题词"""
    PRESET_TO_THEME = {
        "tengu": "天狗",
        "kappa": "河童",
        "kitsune": "九尾狐",
        "yuki_onna": "雪女",
        "oni": "鬼",
        "hyakki_yagyo": "百鬼夜行",
        "tang_beauty": "唐仕女",
        "dunhuang": "飞天",
    }
    return PRESET_TO_THEME.get(preset, preset)


# ============================================================
# 主流程
# ============================================================

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preset", default="tengu")
    ap.add_argument("--category", default="yokai")
    ap.add_argument("--engine", default="pollinations",
                    choices=["pollinations", "agnes", "siliconflow"])
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--format", default="waka",
                    choices=["wuyan", "qiyan", "waka", "haiku", "tiba", "auto"])
    ap.add_argument("--texture", default="xuan_paper",
                    choices=["xuan_paper", "silk", "aged", "brown"])
    ap.add_argument("--strength", type=float, default=0.55)
    ap.add_argument("--no-aging", action="store_true")
    ap.add_argument("--no-inscription", action="store_true")
    ap.add_argument("--no-seal", action="store_true")
    ap.add_argument("--out", default=None)

    # clean-prompt: 默认开启，用 --no-clean-prompt 关闭
    ap.add_argument("--clean-prompt", dest="clean_prompt",
                    action="store_true", default=True,
                    help="从 prompt 移除 inscription 层（默认开启）")
    ap.add_argument("--no-clean-prompt", dest="clean_prompt",
                    action="store_false",
                    help="保留 inscription 层（让 AI 自己画题词印章）")

    args = ap.parse_args()

    print("=" * 70)
    print("  ArtForge 全流程合成")
    print("=" * 70)

    # ---------- 1. Prompt ----------
    from core.prompt_builder import PromptBuilder

    print(f"\n📚 预设: {args.category}/{args.preset}")
    builder = PromptBuilder()
    prompt, detail = builder.compose_preset(
        args.preset, category=args.category, return_detail=True,
    )
    negative = builder.get_negative()

    # 剔除 inscription 层（方案 A）
    if args.clean_prompt and "inscription" in detail:
        removed = detail.pop("inscription")
        parts = [detail[k] for k in builder.LAYER_ORDER if detail.get(k)]
        prompt = ", ".join(parts)
        print(f"\n🧹 已剔除 inscription 层: {removed[:60]}...")
        print(f"   → 题词印章全交 PIL 合成")

    print("\n📋 各层明细:")
    for k, v in detail.items():
        print(f"  [{k:12s}] {v[:60]}")

    # ---------- 2. 出图 ----------
    width, height = pick_size(detail)
    print(f"\n🖼️  画幅: {width}x{height}")

    from api_engines import create_engine

    config = load_config()
    engine = create_engine(args.engine, config)

    print(f"\n🎨 生成中（10-60 秒）...")
    image = engine.generate_single(
        prompt=prompt, negative=negative,
        width=width, height=height, seed=args.seed,
    )
    if image.mode != "RGBA":
        image = image.convert("RGBA")
    print(f"   ✅ 出图: {image.size[0]}x{image.size[1]}")

    # ---------- 3. 做旧 ----------
    if not args.no_aging:
        from services.aging_processor import AgingProcessor
        ap_proc = AgingProcessor(seed=args.seed)
        rgb = image.convert("RGB")
        aged = ap_proc.apply(rgb, texture=args.texture, strength=args.strength)
        image = aged.convert("RGBA")
        print(f"\n📜 做旧: {args.texture} (strength={args.strength})")
    else:
        print("\n📜 做旧: 跳过")

    # ---------- 4. 题词 ----------
    inscription_text = ""
    if not args.no_inscription:
        from services.inscription_generator import InscriptionGenerator

        theme = theme_from_preset(args.preset, args.category)
        ig = InscriptionGenerator(seed=args.seed)
        inscription_text, meta = ig.generate(
            theme=theme, format=args.format, return_meta=True,
        )
        print(f"\n🖋️  题词 ({meta['format_cn']}, source={meta['source']}):")
        for line in inscription_text.split("\n"):
            print(f"   {line}")

        # 渲染到画面（字号放大到 0.045）
        renderer = InscriptionRenderer()
        font_size = max(24, int(min(width, height) * 0.045))
        image = renderer.render(
            image,
            inscription_text,
            font_size=font_size,
            color=(45, 40, 35),
            position="top_right",
            margin=int(min(width, height) * 0.055),
            max_chars_per_col=8,
            bg_alpha=180,
        )
        print(f"   ✅ 已渲染到画面右上角 (font={font_size}, 带底衬)")
    else:
        print("\n🖋️  题词: 跳过")

    # ---------- 5. 印章 ----------
    if not args.no_seal:
        from services.seal_generator import SealGenerator

        sg = SealGenerator()
        theme = theme_from_preset(args.preset, args.category)
        margin = int(min(width, height) * 0.05)

        # 右下：主题印（放大到 0.14）
        image = sg.apply(
            image, theme,
            style="zhu_wen", shape="square",
            position="bottom_right",
            scale=0.14, margin=margin,
        )
        # 左上：引首章（放大到 0.11）
        image = sg.apply(
            image, "ArtForge",
            style="zhu_wen", shape="rect",
            position="top_left",
            scale=0.11, margin=margin,
        )
        print(f"\n🔖 印章: 右下「{theme}」(0.14) + 左上「ArtForge」(0.11)")
    else:
        print("\n🔖 印章: 跳过")

    # ---------- 6. 保存 ----------
    out_dir = PROJECT_ROOT / "output" / args.category
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.out:
        out_path = Path(args.out)
    else:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = out_dir / f"{args.preset}_{ts}.png"

    final = image.convert("RGB")
    final.save(out_path, quality=95)

    # 元信息
    meta_path = out_path.with_suffix(".txt")
    with open(meta_path, "w", encoding="utf-8") as f:
        f.write(f"preset: {args.preset}\n")
        f.write(f"category: {args.category}\n")
        f.write(f"engine: {args.engine}\n")
        f.write(f"seed: {args.seed}\n")
        f.write(f"size: {final.size[0]}x{final.size[1]}\n")
        f.write(f"texture: {args.texture}\n")
        f.write(f"strength: {args.strength}\n")
        f.write(f"clean_prompt: {args.clean_prompt}\n")
        f.write(f"\nprompt:\n{prompt}\n")
        f.write(f"\nnegative:\n{negative}\n")
        f.write(f"\nlayers:\n")
        for k, v in detail.items():
            f.write(f"  {k}: {v}\n")
        if inscription_text:
            f.write(f"\ninscription:\n{inscription_text}\n")

    print(f"\n✅ 成品: {out_path}")
    print(f"📝 元信息: {meta_path}")

    print("\n" + "=" * 70)
    print("  ✅ 全流程完成")
    print("=" * 70)


if __name__ == "__main__":
    main()