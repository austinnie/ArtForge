"""
题词书写 Skill
职责：将题词文本竖排渲染到现有画作上
"""
import sys
from pathlib import Path
from PIL import Image
from typing import Tuple, Optional

# 确保能 import 项目根模块
project_root = Path(__file__).parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 复用 compose_artwork 中成熟的渲染器
from compose_artwork import InscriptionRenderer

class InscriptionWriter:
    """题词书写器"""
    
    def __init__(self):
        self.renderer = InscriptionRenderer()

    def write(
        self,
        image_path: str,
        text: str,
        output_path: str,
        font_size: int = 36,
        color: Tuple[int, int, int] = (45, 40, 35),  # 默认墨色
        position: str = "top_right",
        margin: int = 50,
        max_chars_per_col: int = 8,
    ) -> dict:
        """
        将题词渲染到图片上
        """
        img_path = Path(image_path)
        if not img_path.exists():
            return {"status": "error", "error": f"图片不存在: {img_path}"}
        
        # 加载图片并转为 RGBA
        image = Image.open(img_path).convert("RGBA")
        
        # 自适应参数（如果传入 "auto"）
        if margin == "auto" or isinstance(margin, str):
            margin = int(min(image.size) * 0.05)
        if font_size == "auto" or isinstance(font_size, str):
            font_size = max(24, int(min(image.size) * 0.045))

        # 渲染题词
        result_image = self.renderer.render(
            canvas=image,
            text=text,
            font_size=font_size,
            color=color,
            position=position,
            margin=margin,
            max_chars_per_col=max_chars_per_col,
        )
        
        # 保存输出
        out_path = Path(output_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        result_image.convert("RGB").save(out_path, quality=95)
        
        return {
            "status": "success",
            "result": {
                "output_path": str(out_path),
                "text": text,
                "position": position,
                "font_size": font_size,
            }
        }