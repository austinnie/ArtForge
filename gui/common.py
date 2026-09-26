# gui/common.py
"""GUI 公共工具"""
from __future__ import annotations

import os
import sys
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def load_env_config() -> dict:
    """从 .env / 环境变量读取 API Key，返回给 create_engine 的 config dict。"""
    try:
        from dotenv import load_dotenv
        env_file = PROJECT_ROOT / ".env"
        if env_file.exists():
            load_dotenv(env_file)
        else:
            load_dotenv()
    except ImportError:
        pass

    keys = [
        "POLLINATIONS_API_KEY", "POLLINATIONS_MODEL",
        "POLLINATIONS_VIDEO_MODEL", "POLLINATIONS_AUDIO_MODEL",
        "AGNES_API_KEY", "AGNES_BASE_URL",
        "AGNES_IMAGE_MODEL", "AGNES_TEXT_MODEL",
        "AGNES_VIDEO_MODEL", "AGNES_VISION_MODEL",
        "SILICONFLOW_API_KEY", "SILICONFLOW_MODEL",
        "HF_API_TOKEN", "HF_MODEL",
        "OPENROUTER_API_KEY", "OPENROUTER_MODEL",
    ]
    return {k: os.getenv(k) for k in keys}


def get_preset_map() -> dict:
    """返回 {category: [preset_names]}，用于 UI 下拉。"""
    try:
        from core.prompt_builder import PromptBuilder
        builder = PromptBuilder()
        return builder.list_presets() or {}
    except Exception as e:
        print(f"⚠️ 加载预设失败: {e}")
        return {}


def get_all_themes() -> list:
    """扫描 wechat_formatter/themes/ 下的所有主题名。"""
    themes_dir = PROJECT_ROOT / "skills" / "wechat_formatter" / "themes"
    names = []
    if themes_dir.exists():
        for f in sorted(themes_dir.glob("*.json")):
            names.append(f.stem)
    if not names:
        names = ["newspaper", "terracotta", "bytedance", "chinese",
                 "github", "magazine"]
    return names


def ensure_dir(p) -> Path:
    p = Path(p)
    p.mkdir(parents=True, exist_ok=True)
    return p


def open_dir(path) -> str:
    """跨平台打开目录，返回状态文案。"""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    try:
        if sys.platform == "win32":
            os.startfile(str(p))
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(p)])
        else:
            subprocess.Popen(["xdg-open", str(p)])
        return f"📂 已打开: {p}"
    except Exception as e:
        return f"❌ 打开失败: {e}\n路径: {p}"


def safe_slug(s: str, max_len: int = 40) -> str:
    import re
    s = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", s or "").strip()
    s = re.sub(r"\s+", "_", s)
    return (s[:max_len] or "untitled")