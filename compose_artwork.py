# compose_artwork.py
"""
ArtForge 合成工具库

本文件提供两类内容：

【工具类 / 函数】（被 main.py / GUI / 其他脚本复用）
  - ARTIST_NAME          ：作者名（印章、水印、元信息用）
  - COMPOSITION_SIZE     ：画幅 → 尺寸映射
  - InscriptionRenderer  ：题词竖排渲染器
  - load_config()        ：读 .env → API 配置 dict
  - pick_size()          ：根据 composition 层推画幅尺寸
  - theme_from_preset()  ：根据预设推题词主题

【使用方式】
  from compose_artwork import (
      ARTIST_NAME,
      InscriptionRenderer,
      load_config,
      pick_size,
      theme_from_preset,
  )

【CLI 入口】
  请使用 main.py（唯一 CLI 入口）：
      python main.py --preset tengu --category yokai
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple

from PIL import Image, ImageDraw, ImageFont


# ============================================================
# 个人配置（请修改为你的名字）
# ============================================================
ARTIST_NAME = "东方艺术"  # ✅ 改成你的名字


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
# 题词渲染器（竖排，从右往左）
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
            bg_alpha:          底衬透明度 0-255（0 = 不加底衬）
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
# 工具函数
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
    """
    根据分类 + 预设名推题词主题。

    规则:
      1. 先查显式映射表
      2. 查不到 → 画风类（japanese/gufeng）用「通用」
      3. 再查不到 → 用预设名兜底
    """
    PRESET_TO_THEME = {
        # ---------- yokai ----------
        "tengu":        "天狗",
        "kappa":        "河童",
        "kitsune":      "九尾狐",
        "yuki_onna":    "雪女",
        "oni":          "鬼",
        "hyakki_yagyo": "百鬼夜行",
        "noppera_bo":   "天狗",
        "roku_ro_kubi": "天狗",

        # ---------- genji ----------
        "heian_court":    "观月",
        "junihitoe":      "唐仕女",
        "byobu_emaki":    "观月",
        "moon_viewing":   "观月",
        "cherry_blossom": "赏樱",

        # ---------- tang ----------
        "dunhuang":    "飞天",
        "tang_beauty": "唐仕女",
        "tang_palace": "唐仕女",
        "tang_horse":  "通用",
        "feitian":     "飞天",
    }

    if preset in PRESET_TO_THEME:
        return PRESET_TO_THEME[preset]

    if category in ("japanese", "gufeng"):
        return "通用"

    return preset


# ============================================================
# 自检（确保工具能正常 import）
# ============================================================

if __name__ == "__main__":
    print("=" * 70)
    print("  compose_artwork.py — 工具库自检")
    print("=" * 70)
    print(f"\n🔍 ARTIST_NAME: {ARTIST_NAME}")
    print(f"🔍 COMPOSITION_SIZE: {list(COMPOSITION_SIZE.keys())}")
    print(f"🔍 InscriptionRenderer 字体: ", end="")
    r = InscriptionRenderer()
    print(r.font_path.name if r.font_path else "（默认字体）")
    print(f"🔍 theme_from_preset('tengu', 'yokai'): {theme_from_preset('tengu', 'yokai')}")
    print(f"🔍 theme_from_preset('shui_mo', 'gufeng'): {theme_from_preset('shui_mo', 'gufeng')}")
    print(f"🔍 pick_size({{'composition': 'horizontal'}}): {pick_size({'composition': 'horizontal'})}")
    print(f"🔍 load_config() keys: {list(load_config().keys())}")
    print("\n" + "=" * 70)
    print("  ✅ 工具库自检完成（提示：CLI 请用 main.py）")
    print("=" * 70)