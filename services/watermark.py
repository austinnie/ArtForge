# services/watermark.py
"""防伪水印处理器：斜向平铺 + 描边 + 半透明底块（任何底图可见）"""
from __future__ import annotations
import random
from pathlib import Path
from typing import Optional
from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ARTIST_NAME = "东方艺术"


class WatermarkProcessor:
    def __init__(self, seed: Optional[int] = None):
        self.seed = seed
        self.rng = random.Random(seed)

    def add_subtle_watermark(
        self,
        image: Image.Image,
        text: str,
        opacity: int = 80,             # ← 80 更稳（描边+底块后不刺眼）
        font_size: int = 40,
        angle: int = -30,
        spacing_x: int = 200,
        spacing_y: int = 200,
        font_path: Optional[str] = None,
        stroke: bool = True,
        stroke_width: int = 2,
        bg_block_alpha: int = 30,      # 底块透明度（0=不加底块）
    ) -> Image.Image:
        original_mode = image.mode
        if image.mode != "RGBA":
            image = image.convert("RGBA")

        img_w, img_h = image.size
        diag = int((img_w ** 2 + img_h ** 2) ** 0.5) + 100

        large_layer = Image.new("RGBA", (diag, diag), (0, 0, 0, 0))
        large_draw = ImageDraw.Draw(large_layer)
        font = self._load_font(font_size, font_path)

        bbox = large_draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        y = -text_h
        while y < diag + text_h:
            x = -text_w
            while x < diag + text_w:
                ox = self.rng.randint(-6, 6)
                oy = self.rng.randint(-6, 6)
                px, py = x + ox, y + oy

                # 半透明底块（让水印在任何底图上都有对比）
                if bg_block_alpha > 0:
                    pad = 6
                    large_draw.rectangle(
                        [px - pad, py - pad,
                         px + text_w + pad, py + text_h + pad],
                        fill=(0, 0, 0, bg_block_alpha),
                    )

                # 白色文字 + 黑色描边（或反过来）
                if stroke:
                    large_draw.text(
                        (px, py), text, font=font,
                        fill=(255, 255, 255, opacity),
                        stroke_width=stroke_width,
                        stroke_fill=(0, 0, 0, opacity),
                    )
                else:
                    large_draw.text(
                        (px, py), text, font=font,
                        fill=(255, 255, 255, opacity),
                    )

                x += text_w + spacing_x
            y += text_h + spacing_y

        rotated = large_layer.rotate(
            angle, expand=0, center=(diag // 2, diag // 2),
        )

        cx = (diag - img_w) // 2
        cy = (diag - img_h) // 2
        final_wm = rotated.crop((cx, cy, cx + img_w, cy + img_h))

        result = Image.alpha_composite(image, final_wm)

        if original_mode == "RGB":
            return result.convert("RGB")
        return result

    def _load_font(self, size: int, font_path: Optional[str] = None):
        if font_path and Path(font_path).exists():
            try:
                return ImageFont.truetype(font_path, size)
            except Exception:
                pass

        zhuan_font = PROJECT_ROOT / "assets" / "fonts" / "Mini_zhuan.ttf"
        if zhuan_font.exists():
            try:
                return ImageFont.truetype(str(zhuan_font), size)
            except Exception:
                pass

        for p in [Path("C:/Windows/Fonts/simkai.ttf"),
                  Path("C:/Windows/Fonts/msyh.ttc")]:
            if p.exists():
                try:
                    return ImageFont.truetype(str(p), size)
                except Exception:
                    pass
        return ImageFont.load_default()


if __name__ == "__main__":
    print("=" * 70)
    print("  WatermarkProcessor 自检（描边 + 半透明底块）")
    print("=" * 70)
    test_img = Image.new("RGB", (800, 1200), (240, 235, 220))
    d = ImageDraw.Draw(test_img)
    d.rectangle([0, 400, 800, 800], fill=(60, 40, 30))   # 深色块

    wp = WatermarkProcessor(seed=42)
    result = wp.add_subtle_watermark(test_img, "東方藝術", opacity=80)
    out = PROJECT_ROOT / "output" / "tmp" / "watermark_test.png"
    out.parent.mkdir(exist_ok=True, parents=True)
    result.convert("RGB").save(out)
    print(f"✅ 已保存: {out}")
    print("=" * 70)