"""
ukiyoe_converter - 浮世绘风格转换器
功能：
- 输入普通图片，通过 AI 图生图转换为浮世绘风格
- 自动加盖专属印章（朱文/白文）
- 支持多引擎（Agnes / Pollinations）
"""
import sys
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image

# 确保能 import 项目根模块
project_root = Path(__file__).parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from api_engines import create_engine
from services.seal_generator import SealGenerator
from config.settings import settings

logger = logging.getLogger(__name__)

# 浮世绘风格 Prompt 模板
UKIYOE_PROMPT = (
    "ukiyoe woodblock print, flat colors, bold outlines, "
    "Hokusai and Hiroshige style, visible woodblock grain, "
    "traditional Japanese print, masterpiece, best quality, highly detailed"
)

UKIYOE_NEGATIVE = (
    "3d, realistic, photograph, modern, western style, "
    "blurry, low quality, ugly, deformed, text, watermark"
)


class UkiyoeConverter:
    """浮世绘风格转换器"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.name = "ukiyoe_converter"
        self.version = "1.0.0"
        self._setup_logging()
        self._setup_config()
        self._engine = None
        self._seal_generator = SealGenerator()

    def _setup_logging(self):
        level = self.config.get("log_level", "INFO")
        logging.basicConfig(
            level=getattr(logging, level.upper()),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    def _setup_config(self):
        defaults = {
            "output_dir": "./output/ukiyoe",
            "engine": "pollinations",  # 默认用免费的 Pollinations
            "strength": 0.75,          # 图生图强度（0-1，越大越像浮世绘，越小越像原图）
            "seal_text": "東方藝術",
            "seal_style": "zhu_wen",
            "seal_position": "bottom_right",
        }
        for k, v in defaults.items():
            self.config.setdefault(k, v)
        Path(self.config["output_dir"]).mkdir(parents=True, exist_ok=True)

    def _init_engine(self, engine_name: str = None):
        """初始化图像生成引擎"""
        name = engine_name or self.config["engine"]
        try:
            cfg = settings.get_engine_config(name)
            self._engine = create_engine(name, cfg)
            logger.info(f"✅ 图像引擎已加载: {name}")
        except Exception as e:
            logger.error(f"❌ 引擎加载失败: {e}")
            self._engine = None

    def convert(
        self,
        image_path: str,
        output_path: Optional[str] = None,
        engine_name: Optional[str] = None,
        strength: Optional[float] = None,
        seal_text: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        将图片转换为浮世绘风格并加盖印章

        Args:
            image_path: 输入图片路径
            output_path: 输出图片路径（默认自动生成）
            engine_name: 引擎名称（pollinations / agnes）
            strength: 转换强度（0-1）
            seal_text: 印章文字

        Returns:
            {"status": "success", "result": {...}} 或 {"status": "error", "error": "..."}
        """
        start_time = time.time()
        logger.info(f"执行技能: {self.name} (v{self.version})")

        try:
            # 1. 校验输入
            img_path = Path(image_path).resolve()
            if not img_path.exists():
                return {"status": "error", "error": f"图片不存在: {img_path}"}

            # 2. 初始化引擎
            self._init_engine(engine_name)
            if not self._engine:
                return {"status": "error", "error": "图像引擎不可用"}

            # 3. 检查引擎是否支持图生图
            if not hasattr(self._engine, "image_to_image"):
                return {"status": "error", "error": f"{engine_name} 不支持图生图"}

            # 4. 加载图片
            logger.info(f"🖼️  加载图片: {img_path.name}")
            input_image = Image.open(img_path).convert("RGB")

            # 5. 图生图转换
            eff_strength = strength if strength is not None else self.config["strength"]
            logger.info(f" 开始浮世绘转换 (strength={eff_strength})...")
            
            result_image = self._engine.image_to_image(
                prompt=UKIYOE_PROMPT,
                negative=UKIYOE_NEGATIVE,
                image=input_image,
                strength=eff_strength,
                width=input_image.size[0],
                height=input_image.size[1],
            )

            if result_image is None:
                return {"status": "error", "error": "图生图生成失败"}

            # 6. 加盖印章
            eff_seal_text = seal_text if seal_text is not None else self.config["seal_text"]
            logger.info(f"🔖 加盖印章: {eff_seal_text}")
            
            final_image = self._seal_generator.apply(
                canvas=result_image,
                text=eff_seal_text,
                style=self.config["seal_style"],
                position=self.config["seal_position"],
                scale=0.12,
                margin=40,
            )

            # 7. 保存输出
            if output_path:
                out_path = Path(output_path).resolve()
            else:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                out_path = Path(self.config["output_dir"]) / f"ukiyoe_{img_path.stem}_{timestamp}.png"
            
            out_path.parent.mkdir(parents=True, exist_ok=True)
            final_image.save(out_path, quality=95)
            logger.info(f"✅ 已保存: {out_path}")

            return {
                "status": "success",
                "result": {
                    "output_path": str(out_path),
                    "input_path": str(img_path),
                    "engine": engine_name or self.config["engine"],
                    "strength": eff_strength,
                    "seal_text": eff_seal_text,
                    "elapsed": f"{time.time() - start_time:.2f}s",
                },
                "metadata": {"skill": self.name, "version": self.version},
            }

        except Exception as e:
            logger.error(f"执行失败: {e}")
            import traceback
            traceback.print_exc()
            return {"status": "error", "error": str(e), "skill": self.name}