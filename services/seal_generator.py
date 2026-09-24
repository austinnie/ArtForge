# services/seal_generator.py
"""
印章生成器 — 朱文 / 白文，透明 PNG，支持贴图

用法:
    from services.seal_generator import SealGenerator

    sg = SealGenerator()
    seal = sg.make("鞍马山", style="zhu_wen")       # 朱文（阳刻）
    seal = sg.make("天狗", style="bai_wen")         # 白文（阴刻）
    seal = sg.make("ArtForge", style="zhu_wen", shape="rect")

    sg.paste(image, seal, position="bottom_right", margin=40, scale=0.12)
    image = sg.apply(image, text="鞍马山", style="zhu_wen")
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Optional, Tuple, Union

from PIL import Image, ImageDraw, ImageFont


# ============================================================
# 路径 & 字体
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FONT_DIR = PROJECT_ROOT / "assets" / "fonts"

FONT_CANDIDATES = [
    FONT_DIR / "seal.ttf",          # 项目自带篆书（推荐）
    FONT_DIR / "kai.ttf",
    FONT_DIR / "hanyi_shangwei.ttf",
    Path("C:/Windows/Fonts/simkai.ttf"),
    Path("C:/Windows/Fonts/simsun.ttc"),
    Path("C:/Windows/Fonts/msyh.ttc"),
    Path("C:/Windows/Fonts/simhei.ttf"),
    Path("/System/Library/Fonts/PingFang.ttc"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
]

CINNABAR = (196, 30, 58, 255)     # 朱砂红
PAPER = (252, 250, 240, 255)      # 宣纸白
TRANSPARENT = (0, 0, 0, 0)


# ============================================================
# SealGenerator
# ============================================================

class SealGenerator:
    """印章生成器"""

    def __init__(self, font_path: Optional[Union[str, Path]] = None):
        self.font_path = self._resolve_font(font_path)

    # ---------- 字体 ----------

    def _resolve_font(self, font_path) -> Optional[Path]:
        if font_path:
            p = Path(font_path)
            if p.exists():
                return p
            print(f"   ⚠️ 指定字体不存在: {p}")
        for p in FONT_CANDIDATES:
            if p.exists():
                return p
        print("   ⚠️ 未找到中文字体，将用 Pillow 默认字体")
        return None

    def _load_font(self, size: int) -> ImageFont.FreeTypeFont:
        if self.font_path:
            try:
                return ImageFont.truetype(str(self.font_path), size)
            except Exception as e:
                print(f"   ⚠️ 加载字体失败: {e}")
        return ImageFont.load_default()

    # ---------- 排版：把文字拆成行列 ----------

    @staticmethod
    def _layout_chars(text: str, shape: str) -> list:
        """
        印章排布规则：
          - rect:   横排一行
          - square:
              1 字 → [1]
              2 字 → 竖排（每字一行）
              3 字 → 上1下2
              4 字 → 2x2 田字
              >4 字 → 竖排
        """
        text = text.strip()
        n = len(text)

        if shape == "rect":
            return [list(text)]

        if n == 0:
            return [[]]
        if n == 1:
            return [[text[0]]]
        if n == 2:
            return [[text[0]], [text[1]]]                 # 竖排
        if n == 3:
            return [[text[0]], [text[1], text[2]]]        # 上1下2
        if n == 4:
            return [list(text[:2]), list(text[2:])]       # 2x2
        return [[c] for c in text]                        # 多字竖排

    # ---------- 排版：测量与定位 ----------

    def _plan_glyphs(
        self,
        draw: ImageDraw.ImageDraw,
        lines: list,
        font: ImageFont.FreeTypeFont,
        inner_box: Tuple[int, int, int, int],
        char_gap: int,
        line_gap: int,
    ):
        """
        计算每个字的绝对绘制坐标。

        返回: [(char, (x, y)), ...]，其中 (x, y) 是字的左上角。
        用绝对坐标统一计算，避免逐字累积误差。
        """
        ix0, iy0, ix1, iy1 = inner_box
        inner_w = ix1 - ix0
        inner_h = iy1 - iy0

        # 1. 量每一行的宽高（用统一 bbox 参考）
        line_metrics = []   # [{"w":.., "h":.., "chars":[(ch, cw, ch_h, bbox)]}]
        for line in lines:
            chars = []
            line_w = 0
            line_h = 0
            for i, ch in enumerate(line):
                bbox = draw.textbbox((0, 0), ch, font=font)
                cw = bbox[2] - bbox[0]
                ch_h = bbox[3] - bbox[1]
                chars.append((ch, cw, ch_h, bbox))
                line_w += cw + (char_gap if i < len(line) - 1 else 0)
                line_h = max(line_h, ch_h)
            line_metrics.append({"w": line_w, "h": line_h, "chars": chars})

        # 2. 整个文字块尺寸
        block_h = sum(m["h"] for m in line_metrics) + \
                  line_gap * (len(line_metrics) - 1)

        # 3. 垂直居中起始 y
        y = iy0 + (inner_h - block_h) // 2

        # 4. 逐行安排
        placed = []
        for m in line_metrics:
            # 每行水平居中
            x = ix0 + (inner_w - m["w"]) // 2
            for (ch, cw, ch_h, bbox) in m["chars"]:
                # 补偿 bbox 偏移，让字真正画在 (x, y)
                gx = x - bbox[0]
                gy = y - bbox[1]
                placed.append((ch, (gx, gy)))
                x += cw + char_gap
            y += m["h"] + line_gap

        return placed

    # ---------- 字号自适应 ----------

    def _pick_font_size(
        self,
        shape: str,
        lines: list,
        inner_w: int,
        inner_h: int,
    ) -> int:
        """
        根据印面内框 + 排版，估算字号。

        - rect（横排）：字号由高度决定，但要留 20% 边距
        - square：
            行数 rows = len(lines)
            最大列数 cols = max(len(l) for l in lines)
            字号 ≈ min(inner_w/cols, inner_h/rows) × 0.86
        """
        if shape == "rect":
            # 横排：高度主导，留边
            base = inner_h * 0.68
            # 防止太宽（英文长词）
            text_len = sum(len(l) for l in lines)
            if text_len > 0:
                # 估算平均字宽 ≈ 0.6 字号（英文/数字），中文 ≈ 1.0
                # 保守用 0.7
                est_w_per_font = 0.7
                max_by_width = inner_w / (text_len * est_w_per_font)
                base = min(base, max_by_width * 0.95)
            return max(12, int(base))

        rows = len(lines)
        cols = max((len(l) for l in lines), default=1)

        # 3 字「上1下2」时，下方行有 2 字，宽度可能比高度更紧
        by_h = inner_h / rows
        by_w = inner_w / cols
        base = min(by_h, by_w) * 0.86
        return max(12, int(base))

    # ---------- 核心：生成印章 ----------

    def make(
        self,
        text: str,
        style: str = "zhu_wen",
        shape: str = "square",
        size: int = 256,
        border: int = 8,
    ) -> Image.Image:
        """
        生成印章（RGBA 透明背景）。

        Args:
            text:   印章文字（1-4 字最佳）
            style:  "zhu_wen"（朱文，红字）/ "bai_wen"（白文，红底白字）
            shape:  "square"（方印）/ "rect"（引首章）
            size:   边长（px）
            border: 边框粗细

        Returns:
            RGBA 图像
        """
        style = style.lower()
        shape = shape.lower()

        if style not in ("zhu_wen", "bai_wen"):
            print(f"   ⚠️ 未知印式 '{style}'，使用 zhu_wen")
            style = "zhu_wen"

        # 画布尺寸
        if shape == "rect":
            w, h = size, int(size * 0.45)
        else:
            w = h = size

        # 边框 + 内边距
        pad = border + max(6, size // 22)
        inner_box = (pad, pad, w - pad, h - pad)
        inner_w = inner_box[2] - inner_box[0]
        inner_h = inner_box[3] - inner_box[1]

        img = Image.new("RGBA", (w, h), TRANSPARENT)
        draw = ImageDraw.Draw(img)

        # ---- 底 ----
        if style == "bai_wen":
            draw.rectangle([0, 0, w - 1, h - 1], fill=CINNABAR)
            text_color = PAPER
        else:
            draw.rectangle([0, 0, w - 1, h - 1],
                           outline=CINNABAR, width=border)
            text_color = CINNABAR

        # ---- 排版 ----
        lines = self._layout_chars(text, shape)
        font_size = self._pick_font_size(shape, lines, inner_w, inner_h)
        font = self._load_font(font_size)

        # 字距/行距（负值收紧，让字撑满）
        char_gap = -int(font_size * 0.12)
        line_gap = -int(font_size * 0.10)

        placed = self._plan_glyphs(
            draw, lines, font, inner_box, char_gap, line_gap
        )

        # ---- 绘制 ----
        for ch, (gx, gy) in placed:
            draw.text((gx, gy), ch, font=font, fill=text_color)

        return img

    # ---------- 贴到作品 ----------

    @staticmethod
    def _position_xy(
        canvas_size: Tuple[int, int],
        seal_size: Tuple[int, int],
        position: str,
        margin: int,
    ) -> Tuple[int, int]:
        cw, ch = canvas_size
        sw, sh = seal_size
        position = position.lower()

        x = cw - sw - margin
        y = ch - sh - margin

        if "left" in position:
            x = margin
        if "top" in position:
            y = margin
        elif "center" in position:
            y = (ch - sh) // 2

        x = max(0, min(x, cw - sw))
        y = max(0, min(y, ch - sh))
        return x, y

    def paste(
        self,
        canvas: Image.Image,
        seal: Image.Image,
        position: str = "bottom_right",
        margin: int = 40,
        scale: float = 0.12,
    ) -> Image.Image:
        if canvas.mode != "RGBA":
            canvas = canvas.convert("RGBA")

        cw, ch = canvas.size
        target = max(48, int(min(cw, ch) * scale))

        sw, sh = seal.size
        ratio = target / max(sw, sh)
        new_size = (max(1, int(sw * ratio)), max(1, int(sh * ratio)))
        seal_resized = seal.resize(new_size, Image.Resampling.LANCZOS)

        x, y = self._position_xy((cw, ch), new_size, position, margin)
        canvas.alpha_composite(seal_resized, dest=(x, y))
        return canvas

    def apply(
        self,
        canvas: Image.Image,
        text: str,
        style: str = "zhu_wen",
        position: str = "bottom_right",
        scale: float = 0.12,
        margin: int = 40,
        shape: str = "square",
    ) -> Image.Image:
        cw, ch = canvas.size
        seal_size = max(64, int(min(cw, ch) * scale * 1.6))
        seal = self.make(text, style=style, shape=shape, size=seal_size)
        return self.paste(canvas, seal, position=position,
                          margin=margin, scale=scale)


# ============================================================
# 自检
# ============================================================

if __name__ == "__main__":
    print("=" * 70)
    print("  SealGenerator 自检")
    print("=" * 70)

    sg = SealGenerator()
    print(f"\n🔍 字体: {sg.font_path or '默认字体'}")

    out_dir = PROJECT_ROOT / "output" / "tmp" / "seals"
    out_dir.mkdir(parents=True, exist_ok=True)

    cases = [
        ("鞍马山",  "zhu_wen", "square"),
        ("天狗",    "bai_wen", "square"),
        ("ArtForge","zhu_wen", "rect"),
        ("源氏物语", "bai_wen", "square"),
        ("天",      "zhu_wen", "square"),
        ("百鬼夜行", "bai_wen", "square"),
    ]

    for text, style, shape in cases:
        seal = sg.make(text, style=style, shape=shape, size=256)
        fname = f"{text}_{style}_{shape}.png"
        seal.save(out_dir / fname)
        print(f"  ✅ {fname}  ({seal.size[0]}x{seal.size[1]})")

    # 贴图测试
    test = Image.new("RGBA", (800, 1200), (240, 235, 220, 255))
    test = sg.apply(test, "鞍马山", style="zhu_wen",
                    position="bottom_right", scale=0.12, margin=50)
    test = sg.apply(test, "天狗", style="bai_wen",
                    position="top_left", scale=0.10, margin=50)
    test_path = out_dir / "_paste_test.png"
    test.save(test_path)
    print(f"  ✅ 贴图测试: {test_path}")

    print("\n" + "=" * 70)
    print("  ✅ 自检完成")
    print("=" * 70)