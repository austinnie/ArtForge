# skills/seal_maker/skill.py
"""
seal_maker - 印章制作 Skill
职责：
- 生成独立的透明背景印章 PNG（朱文/白文，方/长方）
- 将印章贴到单张图片上
- 批量将印章贴到整个目录的图片上
底层复用：services/seal_generator.py
"""
import sys
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from PIL import Image

# 确保能 import 项目根模块
project_root = Path(__file__).parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from services.seal_generator import SealGenerator

# 尝试导入全局配置获取 ARTIST_NAME
try:
    from config.settings import settings
    DEFAULT_ARTIST_NAME = getattr(settings, "ARTIST_NAME", "東方藝術")
except Exception:
    DEFAULT_ARTIST_NAME = "東方藝術"

logger = logging.getLogger(__name__)

# 支持的图片格式
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}


class SealMaker:
    """印章制作 Skill"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.name = "seal_maker"
        self.version = "1.0.0"
        self._setup_logging()
        self._setup_config()
        self._generator = SealGenerator()
        logger.info("SealMaker 初始化完成")

    # ---------- 初始化 ----------
    def _setup_logging(self):
        log_level = self.config.get("log_level", "INFO")
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    def _setup_config(self):
        defaults = {
            "output_dir": "./output/seals",
            "default_text": DEFAULT_ARTIST_NAME,
            "default_style": "zhu_wen",  # zhu_wen (朱文) / bai_wen (白文)
            "default_shape": "square",   # square (方印) / rect (引首章)
        }
        for k, v in defaults.items():
            self.config.setdefault(k, v)
        Path(self.config["output_dir"]).mkdir(parents=True, exist_ok=True)

    # ---------- 核心功能 1：生成独立印章 ----------
    def make_seal(
        self,
        text: str = None,
        style: str = None,
        shape: str = None,
        size: int = 256,
        output_path: str = None,
    ) -> Dict[str, Any]:
        """生成独立的透明背景印章 PNG"""
        start_time = time.time()
        text = text or self.config["default_text"]
        style = style or self.config["default_style"]
        shape = shape or self.config["default_shape"]

        try:
            seal = self._generator.make(text, style=style, shape=shape, size=size)
            
            result = {
                "text": text,
                "style": style,
                "shape": shape,
                "size": seal.size,
            }

            if output_path:
                out = Path(output_path).resolve()
                out.parent.mkdir(parents=True, exist_ok=True)
                seal.save(out)
                result["output_path"] = str(out)
                logger.info(f"✅ 印章已保存: {out}")

            return {
                "status": "success",
                "result": result,
                "metadata": {"skill": self.name, "version": self.version, "elapsed": f"{time.time() - start_time:.2f}s"},
            }
        except Exception as e:
            logger.error(f"生成印章失败: {e}")
            return {"status": "error", "error": str(e), "skill": self.name}

    # ---------- 核心功能 2：单张盖章 ----------
    def apply_seal(
        self,
        image_path: str,
        text: str = None,
        position: str = "bottom_right",
        scale: float = 0.12,
        style: str = None,
        shape: str = None,
        margin: int = 40,
        output_path: str = None,
    ) -> Dict[str, Any]:
        """将印章贴到单张图片上"""
        start_time = time.time()
        text = text or self.config["default_text"]
        style = style or self.config["default_style"]
        shape = shape or self.config["default_shape"]

        img_path = Path(image_path).resolve()
        if not img_path.exists():
            return {"status": "error", "error": f"图片不存在: {img_path}"}

        try:
            image = Image.open(img_path).convert("RGBA")
            result_image = self._generator.apply(
                image, text,
                style=style, shape=shape,
                position=position, scale=scale, margin=margin,
            )

            result = {
                "text": text,
                "position": position,
                "size": result_image.size,
            }

            if output_path:
                out = Path(output_path).resolve()
                out.parent.mkdir(parents=True, exist_ok=True)
                result_image.convert("RGB").save(out, quality=95)
                result["output_path"] = str(out)
                logger.info(f"✅ 盖章完成: {out}")

            return {
                "status": "success",
                "result": result,
                "metadata": {"skill": self.name, "version": self.version, "elapsed": f"{time.time() - start_time:.2f}s"},
            }
        except Exception as e:
            logger.error(f"盖章失败: {e}")
            return {"status": "error", "error": str(e), "skill": self.name}

    # ---------- 核心功能 3：批量盖章 ----------
    def batch_apply_seal(
        self,
        input_dir: str,
        output_dir: str = None,
        text: str = None,
        position: str = "bottom_right",
        scale: float = 0.12,
        style: str = None,
        shape: str = None,
        margin: int = 40,
    ) -> Dict[str, Any]:
        """批量将印章贴到目录下的所有图片上"""
        start_time = time.time()
        text = text or self.config["default_text"]
        style = style or self.config["default_style"]
        shape = shape or self.config["default_shape"]

        dir_path = Path(input_dir).resolve()
        if not dir_path.exists() or not dir_path.is_dir():
            return {"status": "error", "error": f"目录不存在: {dir_path}"}

        # 扫描图片
        images = [p for p in sorted(dir_path.iterdir()) if p.is_file() and p.suffix.lower() in IMAGE_EXTS]
        if not images:
            return {"status": "error", "error": f"目录下未找到图片: {dir_path}"}

        # 确定输出目录
        out_dir_path = Path(output_dir).resolve() if output_dir else dir_path.parent / f"{dir_path.name}_sealed"
        out_dir_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"🔄 开始批量盖章: {len(images)} 张图片")
        success_count = 0
        failed_list = []

        for idx, img_file in enumerate(images, 1):
            try:
                image = Image.open(img_file).convert("RGBA")
                result_image = self._generator.apply(
                    image, text,
                    style=style, shape=shape,
                    position=position, scale=scale, margin=margin,
                )
                out_file = out_dir_path / f"{img_file.stem}_sealed{img_file.suffix}"
                result_image.convert("RGB").save(out_file, quality=95)
                success_count += 1
                logger.info(f"  [{idx}/{len(images)}] ✅ {img_file.name}")
            except Exception as e:
                failed_list.append({"file": img_file.name, "error": str(e)})
                logger.warning(f"  [{idx}/{len(images)}] ❌ {img_file.name}: {e}")

        return {
            "status": "success",
            "result": {
                "total": len(images),
                "success": success_count,
                "failed": len(failed_list),
                "failed_list": failed_list,
                "output_dir": str(out_dir_path),
            },
            "metadata": {"skill": self.name, "version": self.version, "elapsed": f"{time.time() - start_time:.2f}s"},
        }

    # ---------- 工具方法 ----------
    def get_name(self) -> str:
        return f"SealMaker (default_text={self.config['default_text']})"

    def __repr__(self):
        return f"<SealMaker(default_text={self.config['default_text']})>"