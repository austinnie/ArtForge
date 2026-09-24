# services/watermark.py
"""
防伪水印处理器
功能：在图像上叠加极低透明度的文字水印（斜向平铺）
特点：
- 视觉上几乎不可见（opacity 极低）
- 放大或调整对比度后可见艺人名字
- 不影响画面整体美感
"""
from __future__ import annotations
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from typing import Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# ============================================================
# 个人配置（请修改为你的名字）
# ============================================================
ARTIST_NAME = "東方藝術"  # ✅ 改成你的名字，如 "李太白"、"Zhang San"

class WatermarkProcessor:
    """防伪水印处理器"""

    def __init__(self, seed: Optional[int] = None):
        self.seed = seed
        self.rng = random.Random(seed)

    def add_subtle_watermark(
        self,
        image: Image.Image,
        text: str,
        opacity: int = 12,          # 透明度 0-255（建议 8-20，越低越隐蔽）
        font_size: int = 40,        # 字号
        angle: int = -30,           # 倾斜角度（负数表示左斜）
        spacing_x: int = 150,       # 水平间距
        spacing_y: int = 150,       # 垂直间距
        font_path: Optional[str] = None,
    ) -> Image.Image:
        """
        添加斜向平铺的极低透明度水印
        """
        if image.mode != "RGBA":
            image = image.convert("RGBA")
        
        # 创建透明图层
        watermark_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark_layer)
        
        # 加载字体
        font = self._load_font(font_size, font_path)
        
        # 获取文字尺寸
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        
        # 计算平铺范围（考虑旋转后的边界）
        img_w, img_h = image.size
        # 扩大绘制范围以覆盖旋转后的空白
        diag = int((img_w**2 + img_h**2)**0.5)
        large_layer = Image.new("RGBA", (diag, diag), (0, 0, 0, 0))
        large_draw = ImageDraw.Draw(large_layer)
        
        # 平铺绘制
        y = 0
        while y < diag:
            x = 0
            while x < diag:
                # 随机微调位置（增加自然感）
                offset_x = self.rng.randint(-10, 10)
                offset_y = self.rng.randint(-10, 10)
                
                # 绘制文字（使用指定透明度）
                large_draw.text(
                    (x + offset_x, y + offset_y),
                    text,
                    font=font,
                    fill=(255, 255, 255, opacity),  # 白色文字，极低透明度
                )
                x += text_w + spacing_x
            y += text_h + spacing_y
        
        # 旋转图层
        rotated_layer = large_layer.rotate(angle, expand=0, center=(diag//2, diag//2))
        
        # 裁剪到原图尺寸并居中
        crop_box = (
            (diag - img_w) // 2,
            (diag - img_h) // 2,
            (diag + img_w) // 2,
            (diag + img_h) // 2,
        )
        final_watermark = rotated_layer.crop(crop_box)
        
        # 合成到原图
        return Image.alpha_composite(image, final_watermark)

    def _load_font(self, size: int, font_path: Optional[str] = None) -> ImageFont.FreeTypeFont:
        """加载字体"""
        if font_path and Path(font_path).exists():
            try:
                return ImageFont.truetype(font_path, size)
            except Exception:
                pass
        
        # 尝试使用小篆字体（与印章一致）
        zhuan_font = PROJECT_ROOT / "assets" / "fonts" / "Mini_zhuan.ttf"
        if zhuan_font.exists():
            try:
                return ImageFont.truetype(str(zhuan_font), size)
            except Exception:
                pass
        
        # 兜底系统字体
        for p in [Path("C:/Windows/Fonts/simkai.ttf"), Path("C:/Windows/Fonts/msyh.ttc")]:
            if p.exists():
                try:
                    return ImageFont.truetype(str(p), size)
                except Exception:
                    pass
        return ImageFont.load_default()


if __name__ == "__main__":
    print("=" * 70)
    print("  WatermarkProcessor 自检")
    print("=" * 70)
    
    # 创建测试图
    test_img = Image.new("RGB", (800, 1200), (240, 235, 220))
    
    # 添加水印
    wp = WatermarkProcessor(seed=42)
    result = wp.add_subtle_watermark(test_img, "{東方藝術} · ArtForge", opacity=15, font_size=30)
    
    # 保存
    out_path = PROJECT_ROOT / "output" / "tmp" / "watermark_test.png"
    out_path.parent.mkdir(exist_ok=True)
    result.convert("RGB").save(out_path)
    print(f"✅ 水印测试图已保存: {out_path}")
    print("   提示：正常看几乎不可见，放大或调高对比度可见「東方藝術 · ArtForge」")
    print("=" * 70)