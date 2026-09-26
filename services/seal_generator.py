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
import os
import sys
from pathlib import Path
from typing import Optional, Tuple, Union

from PIL import Image, ImageDraw, ImageFont


# ============================================================
# 路径 & 字体
# ============================================================
# ============================================================
# 路径修正（让 services/ 下的脚本能 import 项目根模块）
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:      # ← 新增
    sys.path.insert(0, str(PROJECT_ROOT))  # ← 新增
    

FONT_DIR = PROJECT_ROOT / "assets" / "fonts"

FONT_CANDIDATES = [
    FONT_DIR / "Mini_zhuan.ttf",          # 项目自带篆书（推荐）
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

    @staticmethod
    def _has_all_glyphs(font: ImageFont.FreeTypeFont, text: str) -> bool:
        """检查字体是否包含 text 中每个字符的字形"""
        try:
            for ch in text:
                if ch.isspace():
                    continue
                mask = font.getmask(ch)
                if mask.size[0] <= 1 or mask.size[1] <= 1:
                    return False
            return True
        except Exception:
            return False

    def _load_font(self, size: int) -> ImageFont.FreeTypeFont:
        """
        加载字体（带缺字检测）：
        1. 优先小篆（Mini_zhuan.ttf），但检测缺字时 fallback
        2. 再尝试 __init__ 指定的字体
        3. 最后系统字体
        """
        # 1. 小篆优先，但要检查「」四字是否都支持
        zhuan_font = PROJECT_ROOT / "assets" / "fonts" / "Mini_zhuan.ttf"
        if zhuan_font.exists():
            try:
                f = ImageFont.truetype(str(zhuan_font), size)
                if self._has_all_glyphs(f, "东方艺术"):
                    return f
                else:
                    print(f"   ⚠️ 小篆字体缺字，回退系统字体")
            except Exception as e:
                print(f"   ⚠️ 小篆字体加载失败: {e}，回退系统字体")

        # 2. __init__ 指定的字体
        if self.font_path and Path(self.font_path).exists():
            try:
                return ImageFont.truetype(str(self.font_path), size)
            except Exception:
                pass

        # 3. 系统字体兜底（按优先级）
        for p in FONT_CANDIDATES:
            if p.exists():
                try:
                    return ImageFont.truetype(str(p), size)
                except Exception:
                    continue

        # 4. Pillow 默认
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
    # 多样式印章生成
    # ============================================================

    def make_round(
        self,
        text: str,
        style: str = "zhu_wen",
        size: int = 256,
        border: int = 8,
    ) -> Image.Image:
        """圆形印章（朱文/白文）"""
        style = style.lower()
        w = h = size
        img = Image.new("RGBA", (w, h), TRANSPARENT)
        draw = ImageDraw.Draw(img)

        pad = border + max(6, size // 22)
        if style == "bai_wen":
            draw.ellipse([0, 0, w - 1, h - 1], fill=CINNABAR)
            text_color = PAPER
        else:
            draw.ellipse(
                [0, 0, w - 1, h - 1],
                outline=CINNABAR, width=border,
            )
            text_color = CINNABAR

        inner_box = (pad, pad, w - pad, h - pad)
        inner_w = inner_box[2] - inner_box[0]
        inner_h = inner_box[3] - inner_box[1]

        lines = self._layout_chars(text, "square")
        font_size = self._pick_font_size("square", lines, inner_w, inner_h)
        font_size = max(12, int(font_size * 0.85))
        font = self._load_font(font_size)

        char_gap = -int(font_size * 0.12)
        line_gap = -int(font_size * 0.10)

        placed = self._plan_glyphs(
            draw, lines, font, inner_box, char_gap, line_gap,
        )
        for ch, (gx, gy) in placed:
            draw.text((gx, gy), ch, font=font, fill=text_color)

        return img

    def make_ellipse(
        self,
        text: str,
        style: str = "zhu_wen",
        size: int = 256,
        border: int = 8,
    ) -> Image.Image:
        """椭圆印章（横椭圆，适合 2 字/3 字）"""
        w = size
        h = int(size * 0.7)
        img = Image.new("RGBA", (w, h), TRANSPARENT)
        draw = ImageDraw.Draw(img)

        pad = border + max(6, size // 22)
        if style == "bai_wen":
            draw.ellipse([0, 0, w - 1, h - 1], fill=CINNABAR)
            text_color = PAPER
        else:
            draw.ellipse(
                [0, 0, w - 1, h - 1],
                outline=CINNABAR, width=border,
            )
            text_color = CINNABAR

        inner_box = (pad, pad, w - pad, h - pad)
        inner_w = inner_box[2] - inner_box[0]
        inner_h = inner_box[3] - inner_box[1]

        lines = self._layout_chars(text, "square")
        font_size = self._pick_font_size("square", lines, inner_w, inner_h)
        font_size = max(12, int(font_size * 0.82))
        font = self._load_font(font_size)

        char_gap = -int(font_size * 0.12)
        line_gap = -int(font_size * 0.10)

        placed = self._plan_glyphs(
            draw, lines, font, inner_box, char_gap, line_gap,
        )
        for ch, (gx, gy) in placed:
            draw.text((gx, gy), ch, font=font, fill=text_color)

        return img

    def make_double_border(
        self,
        text: str,
        style: str = "zhu_wen",
        size: int = 256,
        border: int = 6,
        gap: int = 6,
    ) -> Image.Image:
        """双边框印章（仿古"印中印"）"""
        style = style.lower()
        w = h = size
        img = Image.new("RGBA", (w, h), TRANSPARENT)
        draw = ImageDraw.Draw(img)

        # 外框
        if style == "bai_wen":
            draw.rectangle([0, 0, w - 1, h - 1], fill=CINNABAR)
            text_color = PAPER
            draw.rectangle(
                [border + gap, border + gap,
                 w - border - gap - 1, h - border - gap - 1],
                outline=CINNABAR, width=border,
            )
        else:
            # 朱文：双红线
            draw.rectangle(
                [0, 0, w - 1, h - 1],
                outline=CINNABAR, width=border,
            )
            draw.rectangle(
                [border + gap, border + gap,
                 w - border - gap - 1, h - border - gap - 1],
                outline=CINNABAR, width=max(2, border // 2),
            )
            text_color = CINNABAR

        pad = border * 2 + gap + max(8, size // 18)
        inner_box = (pad, pad, w - pad, h - pad)
        inner_w = inner_box[2] - inner_box[0]
        inner_h = inner_box[3] - inner_box[1]

        lines = self._layout_chars(text, "square")
        font_size = self._pick_font_size("square", lines, inner_w, inner_h)
        font = self._load_font(font_size)

        char_gap = -int(font_size * 0.12)
        line_gap = -int(font_size * 0.10)

        placed = self._plan_glyphs(
            draw, lines, font, inner_box, char_gap, line_gap,
        )
        for ch, (gx, gy) in placed:
            draw.text((gx, gy), ch, font=font, fill=text_color)

        return img

    def make_with_corner_marks(
        self,
        text: str,
        style: str = "zhu_wen",
        size: int = 256,
        border: int = 6,
    ) -> Image.Image:
        """四角带装饰的印章（四灵印风格）"""
        style = style.lower()
        w = h = size
        img = Image.new("RGBA", (w, h), TRANSPARENT)
        draw = ImageDraw.Draw(img)

        # 边框
        if style == "bai_wen":
            draw.rectangle([0, 0, w - 1, h - 1], fill=CINNABAR)
            text_color = PAPER
        else:
            draw.rectangle(
                [0, 0, w - 1, h - 1],
                outline=CINNABAR, width=border,
            )
            text_color = CINNABAR

        # 四角小装饰（小方块）
        mark_size = max(4, size // 32)
        m = border + max(2, size // 60)
        corners = [
            (m, m),
            (w - m - mark_size, m),
            (m, h - m - mark_size),
            (w - m - mark_size, h - m - mark_size),
        ]
        for (cx, cy) in corners:
            draw.rectangle(
                [cx, cy, cx + mark_size, cy + mark_size],
                fill=text_color if style == "zhu_wen" else CINNABAR,
            )

        pad = border + mark_size + max(10, size // 16)
        inner_box = (pad, pad, w - pad, h - pad)
        inner_w = inner_box[2] - inner_box[0]
        inner_h = inner_box[3] - inner_box[1]

        lines = self._layout_chars(text, "square")
        font_size = self._pick_font_size("square", lines, inner_w, inner_h)
        font = self._load_font(font_size)

        char_gap = -int(font_size * 0.12)
        line_gap = -int(font_size * 0.10)

        placed = self._plan_glyphs(
            draw, lines, font, inner_box, char_gap, line_gap,
        )
        for ch, (gx, gy) in placed:
            draw.text((gx, gy), ch, font=font, fill=text_color)

        return img

    # ============================================================
    # 一次生成"品牌印章全套"
    # ============================================================

    def make_all_styles(
        self,
        text: str,
        size: int = 512,
    ) -> dict:
        """
        为同一品牌（如「东方艺术」）生成所有印章样式。

        Returns:
            {
                "square_zhu":       方形·朱文
                "square_bai":       方形·白文
                "square_double":    方形·双边框·朱文
                "square_corner":    方形·四角装饰·朱文
                "rect_zhu":         长方形·朱文（引首章）
                "rect_bai":         长方形·白文
                "round_zhu":        圆形·朱文
                "round_bai":        圆形·白文
                "ellipse_zhu":      椭圆·朱文
            }
        """
        return {
            "square_zhu":     self.make(text, "zhu_wen", "square", size),
            "square_bai":     self.make(text, "bai_wen", "square", size),
            "square_double":  self.make_double_border(text, "zhu_wen", size),
            "square_corner":  self.make_with_corner_marks(text, "zhu_wen", size),
            "rect_zhu":       self.make(text, "zhu_wen", "rect", size),
            "rect_bai":       self.make(text, "bai_wen", "rect", size),
            "round_zhu":      self.make_round(text, "zhu_wen", size),
            "round_bai":      self.make_round(text, "bai_wen", size),
            "ellipse_zhu":    self.make_ellipse(text, "zhu_wen", size),
        }
        
    # ============================================================
    # 方案化钤印（一键贴全套）
    # ============================================================

    # 预定义方案
    SIGNATURE_SCHEMES = {
        "classic": {
            "name": "传统经典",
            "desc": "右下朱文方 + 左上朱文长方",
            "seals": [
                {"pos": "bottom_right", "style": "zhu_wen",
                 "shape": "square", "scale": 0.14},
                {"pos": "top_left", "style": "zhu_wen",
                 "shape": "rect", "scale": 0.11},
            ],
        },
        "contrast": {
            "name": "对比鲜明",
            "desc": "右下白文方 + 左上朱文长方",
            "seals": [
                {"pos": "bottom_right", "style": "bai_wen",
                 "shape": "square", "scale": 0.14},
                {"pos": "top_left", "style": "zhu_wen",
                 "shape": "rect", "scale": 0.11},
            ],
        },
        "luxury": {
            "name": "华丽大气",
            "desc": "右下双边框 + 左上朱文长方 + 左下圆印",
            "seals": [
                {"pos": "bottom_right", "style": "double",
                 "shape": "square", "scale": 0.14},
                {"pos": "top_left", "style": "zhu_wen",
                 "shape": "rect", "scale": 0.11},
                {"pos": "bottom_left", "style": "zhu_wen",
                 "shape": "round", "scale": 0.09},
            ],
        },
        "minimal": {
            "name": "简洁",
            "desc": "只有右下朱文方印",
            "seals": [
                {"pos": "bottom_right", "style": "zhu_wen",
                 "shape": "square", "scale": 0.16},
            ],
        },
    }

    def apply_scheme(
        self,
        canvas: Image.Image,
        text: str,
        scheme: str = "contrast",
        margin_ratio: float = 0.05,
    ) -> Image.Image:
        """
        按预设方案一键贴全套印章。

        Args:
            canvas:        画布
            text:          印章文字（如「东方艺术」）
            scheme:        "classic" | "contrast" | "luxury" | "minimal"
            margin_ratio:  边距相对短边的比例

        Returns:
            合成后的画布
        """
        if scheme not in self.SIGNATURE_SCHEMES:
            print(f"   ⚠️ 未知印章方案 '{scheme}'，使用 contrast")
            scheme = "contrast"

        cfg = self.SIGNATURE_SCHEMES[scheme]
        cw, ch = canvas.size
        margin = int(min(cw, ch) * margin_ratio)

        print(f"   🔖 钤印方案: {cfg['name']} — {cfg['desc']}")

        for item in cfg["seals"]:
            style = item["style"]
            shape = item["shape"]

            # 特殊处理：双边框
            if style == "double":
                cw_cur, ch_cur = canvas.size
                seal_size = max(64, int(min(cw_cur, ch_cur)
                                        * item["scale"] * 1.6))
                seal_img = self.make_double_border(
                    text, "zhu_wen", size=seal_size,
                )
                canvas = self.paste(
                    canvas, seal_img,
                    position=item["pos"],
                    margin=margin,
                    scale=item["scale"],
                )
                continue

            # 特殊处理：圆形
            if shape == "round":
                cw_cur, ch_cur = canvas.size
                seal_size = max(64, int(min(cw_cur, ch_cur)
                                        * item["scale"] * 1.6))
                seal_img = self.make_round(
                    text, style=style, size=seal_size,
                )
                canvas = self.paste(
                    canvas, seal_img,
                    position=item["pos"],
                    margin=margin,
                    scale=item["scale"],
                )
                continue

            # 常规：方/长方
            canvas = self.apply(
                canvas, text,
                style=style, shape=shape,
                position=item["pos"],
                scale=item["scale"],
                margin=margin,
            )

        return canvas        
# ============================================================
# 自检
# ============================================================

if __name__ == "__main__":
    print("=" * 70)
    print("  SealGenerator 自检 — 东方艺术 品牌印章全套")
    print("=" * 70)

    zhuan_font = PROJECT_ROOT / "assets" / "fonts" / "Mini_zhuan.ttf"
    sg = SealGenerator(font_path=zhuan_font if zhuan_font.exists() else None)
    print(f"\n🔍 字体: {sg.font_path or '默认字体'}")

    BRAND = "东方艺术"
    out_dir = PROJECT_ROOT / "output" / "tmp" / "seals"
    out_dir.mkdir(parents=True, exist_ok=True)

    # ============================================================
    # 1. 基础印章（方/长，朱文/白文）
    # ============================================================
    print("\n【1】基础印章")
    base_cases = [
        (BRAND, "zhu_wen", "square"),
        (BRAND, "bai_wen", "square"),
        (BRAND, "zhu_wen", "rect"),
        (BRAND, "bai_wen", "rect"),
    ]
    for text, style, shape in base_cases:
        seal = sg.make(text, style=style, shape=shape, size=384)
        fname = f"brand_{style}_{shape}.png"
        seal.save(out_dir / fname)
        print(f"  ✅ {fname}  ({seal.size[0]}x{seal.size[1]})")

    # ============================================================
    # 2. 多样式印章（圆/椭圆/双边框/四角）
    # ============================================================
    print("\n【2】多样式印章")
    seals = {}
    try:
        seals["round_zhu"] = sg.make_round(BRAND, "zhu_wen", 384)
        seals["round_bai"] = sg.make_round(BRAND, "bai_wen", 384)
        print("  ✅ round_zhu / round_bai")
    except AttributeError:
        print("  ⚠️ make_round 未定义，跳过圆形印")

    try:
        seals["ellipse_zhu"] = sg.make_ellipse(BRAND, "zhu_wen", 384)
        print("  ✅ ellipse_zhu")
    except AttributeError:
        print("  ⚠️ make_ellipse 未定义，跳过椭圆印")

    try:
        seals["double_border"] = sg.make_double_border(BRAND, "zhu_wen", 384)
        print("  ✅ double_border")
    except AttributeError:
        print("  ⚠️ make_double_border 未定义，跳过双边框印")

    try:
        seals["corner_marks"] = sg.make_with_corner_marks(BRAND, "zhu_wen", 384)
        print("  ✅ corner_marks")
    except AttributeError:
        print("  ⚠️ make_with_corner_marks 未定义，跳过四角装饰印")

    for name, img in seals.items():
        fname = f"brand_{name}.png"
        img.save(out_dir / fname)

    # ============================================================
    # 3. 一次生成全套（如果定义了 make_all_styles）
    # ============================================================
    print("\n【3】全套品牌印章")
    try:
        all_seals = sg.make_all_styles(BRAND, size=384)
        for name, img in all_seals.items():
            fname = f"all_{name}.png"
            img.save(out_dir / fname)
        print(f"  ✅ 共生成 {len(all_seals)} 种印章")
    except AttributeError:
        print("  ⚠️ make_all_styles 未定义，跳过（可选用）")

    # ============================================================
    # 4. 贴图测试 — 东方艺术出现在画面各处
    # ============================================================
    print("\n【4】贴图测试（多种钤印方案）")

    # 画幅 1：传统双印（右下主题 + 左上引首）
    canvas1 = Image.new("RGBA", (800, 1200), (240, 235, 220, 255))
    canvas1 = sg.apply(
        canvas1, BRAND,
        style="zhu_wen", shape="square",
        position="bottom_right", scale=0.14, margin=50,
    )
    canvas1 = sg.apply(
        canvas1, BRAND,
        style="zhu_wen", shape="rect",
        position="top_left", scale=0.11, margin=50,
    )
    p1 = out_dir / "_apply_classic.png"
    canvas1.save(p1)
    print(f"  ✅ 传统双印（右下主题 + 左上引首）: {p1}")

    # 画幅 2：白文主题 + 朱文引首
    canvas2 = Image.new("RGBA", (800, 1200), (240, 235, 220, 255))
    canvas2 = sg.apply(
        canvas2, BRAND,
        style="bai_wen", shape="square",
        position="bottom_right", scale=0.14, margin=50,
    )
    canvas2 = sg.apply(
        canvas2, BRAND,
        style="zhu_wen", shape="rect",
        position="top_left", scale=0.11, margin=50,
    )
    p2 = out_dir / "_apply_bai_zhu.png"
    canvas2.save(p2)
    print(f"  ✅ 白文主题 + 朱文引首: {p2}")

    # 画幅 3：四方钤印（四角都有印）
    canvas3 = Image.new("RGBA", (800, 1200), (240, 235, 220, 255))
    canvas3 = sg.apply(
        canvas3, BRAND, style="zhu_wen", shape="square",
        position="bottom_right", scale=0.14, margin=50,
    )
    canvas3 = sg.apply(
        canvas3, BRAND, style="zhu_wen", shape="rect",
        position="top_left", scale=0.11, margin=50,
    )
    canvas3 = sg.apply(
        canvas3, BRAND, style="bai_wen", shape="square",
        position="bottom_left", scale=0.10, margin=50,
    )
    canvas3 = sg.apply(
        canvas3, BRAND, style="zhu_wen", shape="rect",
        position="top_right", scale=0.10, margin=50,
    )
    p3 = out_dir / "_apply_four_corners.png"
    canvas3.save(p3)
    print(f"  ✅ 四角钤印: {p3}")

    # 画幅 4：单主题印（最简）
    canvas4 = Image.new("RGBA", (800, 1200), (240, 235, 220, 255))
    canvas4 = sg.apply(
        canvas4, BRAND,
        style="zhu_wen", shape="square",
        position="bottom_right", scale=0.16, margin=50,
    )
    p4 = out_dir / "_apply_single.png"
    canvas4.save(p4)
    print(f"  ✅ 单个主题印: {p4}")

    # ============================================================
    # 5. 全部印章总览图（3xN 网格）
    # ============================================================
    print("\n【5】生成总览图")

    # 收集所有基础 + 多样式印章
    overview_items = []
    for text, style, shape in base_cases:
        img = sg.make(BRAND, style=style, shape=shape, size=256)
        label = f"{style}_{shape}"
        overview_items.append((label, img))

    for name, img in seals.items():
        overview_items.append((name, img.resize((256, 256), Image.Resampling.LANCZOS)))

    cols = 4
    rows = (len(overview_items) + cols - 1) // cols
    cell = 280
    overview = Image.new("RGB", (cols * cell, rows * cell), (250, 248, 240))

    for i, (label, img) in enumerate(overview_items):
        r, c = divmod(i, cols)
        x = c * cell + (cell - img.size[0]) // 2
        y = r * cell + (cell - img.size[1]) // 2
        overview.paste(img, (x, y), img)

    overview_path = out_dir / "_overview_grid.png"
    overview.save(overview_path)
    print(f"  ✅ 总览图（{len(overview_items)} 种印章）: {overview_path}")

    print("\n" + "=" * 70)
    print(f"  ✅ 自检完成 — 所有印章均为品牌「{BRAND}」")
    print(f"  📂 输出目录: {out_dir}")
    print("=" * 70)