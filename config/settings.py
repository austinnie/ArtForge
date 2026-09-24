# config/settings.py
"""
ArtForge 全局配置

职责：
  - 读取 .env 环境变量
  - 提供统一的配置访问入口
  - 暴露项目路径常量
  - 提供 API 配置的字典访问

使用：
    from config.settings import settings

    settings.agnes_api_key
    settings.default_engine
    settings.output_dir
    settings.get_api_config()
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from dotenv import load_dotenv
    _DOTENV_AVAILABLE = True
except ImportError:
    _DOTENV_AVAILABLE = False
    print("⚠️ python-dotenv 未安装，.env 文件将不会被自动加载")


# ============================================================
# 项目路径
# ============================================================

# config/settings.py → parents[1] = 项目根
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# 加载 .env
ENV_FILE = PROJECT_ROOT / ".env"
if _DOTENV_AVAILABLE and ENV_FILE.exists():
    load_dotenv(ENV_FILE)


# ============================================================
# Settings 类
# ============================================================

class Settings:
    """ArtForge 全局配置"""

    # ---------- 项目路径 ----------
    project_root: Path = PROJECT_ROOT

    # ---------- 目录 ----------
    @property
    def output_dir(self) -> Path:
        d = self._env_path("OUTPUT_DIR", "output")
        d.mkdir(parents=True, exist_ok=True)
        return d

    @property
    def assets_dir(self) -> Path:
        return self.project_root / "assets"

    @property
    def seals_dir(self) -> Path:
        return self.assets_dir / "seals"

    @property
    def textures_dir(self) -> Path:
        return self.assets_dir / "textures"

    @property
    def fonts_dir(self) -> Path:
        return self.assets_dir / "fonts"

    @property
    def presets_dir(self) -> Path:
        return self.project_root / "presets"

    @property
    def logs_dir(self) -> Path:
        d = self.project_root / "logs"
        d.mkdir(parents=True, exist_ok=True)
        return d

    # ---------- 生成模式 ----------
    @property
    def generation_mode(self) -> str:
        """生成模式：api / local"""
        return self._env_str("GENERATION_MODE", "api").lower()

    @property
    def default_engine(self) -> str:
        """默认 API 引擎"""
        return self._env_str("DEFAULT_ENGINE", "agnes").lower()

    # ---------- 默认生成参数 ----------
    @property
    def default_width(self) -> int:
        return self._env_int("DEFAULT_WIDTH", 1024)

    @property
    def default_height(self) -> int:
        return self._env_int("DEFAULT_HEIGHT", 1024)

    @property
    def default_steps(self) -> int:
        return self._env_int("DEFAULT_STEPS", 25)

    @property
    def default_cfg(self) -> float:
        return self._env_float("DEFAULT_CFG", 7.5)

    @property
    def default_scroll(self) -> str:
        """默认画幅（中文）"""
        return self._env_str("DEFAULT_SCROLL", "立轴")

    @property
    def default_inscription(self) -> str:
        """默认题词格式"""
        return self._env_str("DEFAULT_INSCRIPTION", "waka")

    @property
    def default_seal_position(self) -> str:
        """默认印章位置"""
        return self._env_str("DEFAULT_SEAL_POSITION", "左下")

    @property
    def default_texture(self) -> str:
        """默认纸张纹理"""
        return self._env_str("DEFAULT_TEXTURE", "xuan_paper")

    # ---------- 安全 ----------
    @property
    def safe_mode(self) -> bool:
        """是否启用安全模式"""
        return self._env_bool("SAFE_MODE", True)

    @property
    def enable_safety_check(self) -> bool:
        """是否启用安全检测"""
        return self._env_bool("ENABLE_SAFETY_CHECK", True)

    @property
    def allow_art_nude(self) -> bool:
        """是否允许艺术裸体主题（默认关闭，需显式开启）"""
        return self._env_bool("ALLOW_ART_NUDE", False)

    # ---------- LLM（题词生成） ----------
    @property
    def llm_enabled(self) -> bool:
        """是否启用 LLM 生成题词"""
        return self._env_bool("LLM_ENABLED", True)

    @property
    def llm_backends(self) -> list:
        """LLM 后端优先级列表"""
        raw = self._env_str("LLM_BACKENDS", "agnes,ollama")
        return [b.strip() for b in raw.split(",") if b.strip()]

    @property
    def ollama_url(self) -> str:
        return self._env_str("OLLAMA_URL", "http://localhost:11434").rstrip("/")

    @property
    def ollama_model(self) -> str:
        return self._env_str("OLLAMA_MODEL", "qwen2.5:7b")

    @property
    def llm_timeout(self) -> int:
        return self._env_int("LLM_TIMEOUT", 120)

    @property
    def llm_temperature(self) -> float:
        return self._env_float("LLM_TEMPERATURE", 0.7)

    @property
    def llm_max_tokens(self) -> int:
        return self._env_int("LLM_MAX_TOKENS", 2048)

    # ---------- API Keys ----------
    @property
    def agnes_api_key(self) -> Optional[str]:
        return os.environ.get("AGNES_API_KEY")

    @property
    def agnes_base_url(self) -> str:
        return self._env_str("AGNES_BASE_URL", "https://apihub.agnes-ai.com/v1")

    @property
    def agnes_image_model(self) -> str:
        return self._env_str("AGNES_IMAGE_MODEL", "agnes-image-2.1-flash")

    @property
    def agnes_text_model(self) -> str:
        return self._env_str("AGNES_TEXT_MODEL", "agnes-2.5-flash")

    @property
    def agnes_vision_model(self) -> str:
        return self._env_str("AGNES_VISION_MODEL", "agnes-2.5-flash")

    @property
    def pollinations_model(self) -> str:
        return self._env_str("POLLINATIONS_MODEL", "flux")

    @property
    def pollinations_api_key(self) -> Optional[str]:
        return os.environ.get("POLLINATIONS_API_KEY")

    @property
    def siliconflow_api_key(self) -> Optional[str]:
        return os.environ.get("SILICONFLOW_API_KEY")

    @property
    def siliconflow_model(self) -> str:
        return self._env_str("SILICONFLOW_MODEL", "sd-turbo")

    @property
    def hf_api_token(self) -> Optional[str]:
        return os.environ.get("HF_API_TOKEN")

    @property
    def hf_model(self) -> str:
        return self._env_str("HF_MODEL", "sdxl")

    @property
    def replicate_api_token(self) -> Optional[str]:
        return os.environ.get("REPLICATE_API_TOKEN")

    @property
    def stability_api_key(self) -> Optional[str]:
        return os.environ.get("STABILITY_API_KEY")

    # ---------- 后处理 ----------
    @property
    def default_font(self) -> str:
        """题词用的默认字体文件名（放在 assets/fonts/ 下）"""
        return self._env_str("DEFAULT_FONT", "kaiti.ttf")

    @property
    def seal_size_ratio(self) -> float:
        """印章相对画面短边的比例"""
        return self._env_float("SEAL_SIZE_RATIO", 0.06)

    @property
    def inscription_size_ratio(self) -> float:
        """题词文字相对画面短边的比例"""
        return self._env_float("INSCRIPTION_SIZE_RATIO", 0.025)

    # ---------- 微信推送（可选） ----------
    @property
    def wechat_app_id(self) -> Optional[str]:
        return os.environ.get("WECHAT_APP_ID")

    @property
    def wechat_app_secret(self) -> Optional[str]:
        return os.environ.get("WECHAT_APP_SECRET")

    # ---------- 调试 ----------
    @property
    def debug(self) -> bool:
        return self._env_bool("DEBUG", False)

    @property
    def log_level(self) -> str:
        return self._env_str("LOG_LEVEL", "INFO").upper()

    # ============================================================
    # 工具方法
    # ============================================================

    def _env_str(self, key: str, default: str = "") -> str:
        return os.environ.get(key, default)

    def _env_int(self, key: str, default: int = 0) -> int:
        try:
            return int(os.environ.get(key, default))
        except (ValueError, TypeError):
            return default

    def _env_float(self, key: str, default: float = 0.0) -> float:
        try:
            return float(os.environ.get(key, default))
        except (ValueError, TypeError):
            return default

    def _env_bool(self, key: str, default: bool = False) -> bool:
        val = os.environ.get(key)
        if val is None:
            return default
        return val.strip().lower() in ("1", "true", "yes", "on", "y")

    def _env_path(self, key: str, default: str) -> Path:
        """读路径，相对路径自动拼到项目根"""
        val = os.environ.get(key, default)
        p = Path(val)
        if not p.is_absolute():
            p = self.project_root / p
        return p.resolve()

    # ---------- API 配置字典 ----------

    def get_api_config(self) -> Dict[str, Dict[str, Any]]:
        """
        返回所有 API 提供商的配置字典。

        用于传给 api_engines.create_engine(provider, config)。
        """
        return {
            "agnes": {
                "AGNES_API_KEY": self.agnes_api_key,
                "AGNES_BASE_URL": self.agnes_base_url,
                "AGNES_IMAGE_MODEL": self.agnes_image_model,
                "AGNES_TEXT_MODEL": self.agnes_text_model,
                "AGNES_VISION_MODEL": self.agnes_vision_model,
            },
            "pollinations": {
                "POLLINATIONS_API_KEY": self.pollinations_api_key,
                "POLLINATIONS_MODEL": self.pollinations_model,
            },
            "siliconflow": {
                "SILICONFLOW_API_KEY": self.siliconflow_api_key,
                "SILICONFLOW_MODEL": self.siliconflow_model,
            },
            "huggingface": {
                "HF_API_TOKEN": self.hf_api_token,
                "HF_MODEL": self.hf_model,
            },
            "replicate": {
                "REPLICATE_API_TOKEN": self.replicate_api_token,
            },
            "stability": {
                "STABILITY_API_KEY": self.stability_api_key,
            },
        }

    def get_engine_config(self, provider: str) -> Dict[str, Any]:
        """获取单个引擎的配置。"""
        return self.get_api_config().get(provider, {})

    # ---------- 目录自检 ----------

    def ensure_dirs(self) -> None:
        """确保关键目录存在。"""
        for d in [
            self.output_dir,
            self.logs_dir,
            self.seals_dir,
            self.textures_dir,
            self.fonts_dir,
        ]:
            d.mkdir(parents=True, exist_ok=True)

    # ---------- 摘要 ----------

    def summary(self) -> str:
        """返回配置摘要（用于日志/调试）"""
        lines = [
            "=" * 60,
            "  ArtForge 配置摘要",
            "=" * 60,
            f"  项目根目录  : {self.project_root}",
            f"  输出目录    : {self.output_dir}",
            f"  生成模式    : {self.generation_mode}",
            f"  默认引擎    : {self.default_engine}",
            f"  默认画幅    : {self.default_scroll}",
            f"  默认尺寸    : {self.default_width} x {self.default_height}",
            f"  安全模式    : {'开' if self.safe_mode else '关'}",
            f"  艺术裸体    : {'允许' if self.allow_art_nude else '禁止'}",
            f"  LLM 启用    : {'是' if self.llm_enabled else '否'}",
            f"  LLM 后端    : {self.llm_backends}",
            f"  日志级别    : {self.log_level}",
            "=" * 60,
        ]
        return "\n".join(lines)

    def check_api_keys(self) -> Dict[str, bool]:
        """检查各 API Key 是否已配置。"""
        return {
            "agnes": bool(self.agnes_api_key),
            "pollinations": True,  # 无需 Key
            "siliconflow": bool(self.siliconflow_api_key),
            "huggingface": bool(self.hf_api_token),
            "replicate": bool(self.replicate_api_token),
            "stability": bool(self.stability_api_key),
        }


# ============================================================
# 单例
# ============================================================

settings = Settings()


# ============================================================
# 自检
# ============================================================

if __name__ == "__main__":
    import sys

    print(settings.summary())

    print("\n🔑 API Key 检查:")
    for name, ok in settings.check_api_keys().items():
        mark = "✅" if ok else "❌"
        print(f"  {mark} {name}")

    print("\n📁 目录检查:")
    for name in ["project_root", "output_dir", "assets_dir",
                 "seals_dir", "textures_dir", "fonts_dir", "logs_dir"]:
        p = getattr(settings, name)
        exists = "✅" if Path(p).exists() else "⏳"
        print(f"  {exists} {name}: {p}")

    print("\n🎨 默认参数:")
    print(f"  画幅     : {settings.default_scroll}")
    print(f"  尺寸     : {settings.default_width} x {settings.default_height}")
    print(f"  步数     : {settings.default_steps}")
    print(f"  CFG      : {settings.default_cfg}")
    print(f"  题词格式 : {settings.default_inscription}")
    print(f"  印章位置 : {settings.default_seal_position}")
    print(f"  纸张纹理 : {settings.default_texture}")
    print(f"  字体     : {settings.default_font}")
    print(f"  印章比例 : {settings.seal_size_ratio}")
    print(f"  题词比例 : {settings.inscription_size_ratio}")

    print("\n" + "=" * 60)
    print("  ✅ 自检完成")
    print("=" * 60)