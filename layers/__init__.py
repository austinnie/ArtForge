# layers/__init__.py
"""
ArtForge 6 层提示词系统

层级顺序（组合时按这个顺序拼接）：
  1. subject      主体    天狗、九尾狐、唐仕女、艺伎
  2. scene        场景    山林、宫廷、温泉、街道
  3. style        画风    浮世绘、日本画、水墨、敦煌
  4. lighting     光影    月光、烛火、晨雾、夕阳
  5. composition  画幅    立轴、横卷、屏风、团扇
  6. inscription  题词印章 书法、落款、朱印、做旧
  7. quality      画质    masterpiece, 8k, detailed

注：叫「6 层」是沿用 LayerForge 的命名习惯，实际是 7 层。
"""

from typing import Dict, List


# 层级顺序（组合时按此顺序）
LAYER_ORDER = [
    "subject",
    "scene",
    "style",
    "lighting",
    "composition",
    "inscription",
    "quality",
]

# 层级中文名
LAYER_NAMES_CN = {
    "subject": "主体",
    "scene": "场景",
    "style": "画风",
    "lighting": "光影",
    "composition": "画幅",
    "inscription": "题词印章",
    "quality": "画质",
}

# 层级优先级（数字越大越重要，截断时优先保留）
LAYER_PRIORITY = {
    "subject": 100,
    "scene": 80,
    "style": 70,
    "lighting": 50,
    "composition": 40,
    "inscription": 30,
    "quality": 20,
}


def load_all_layers() -> Dict[str, List[str]]:
    """
    加载所有 6 层。

    Returns:
        {
            "subject": [...],
            "scene": [...],
            "style": [...],
            "lighting": [...],
            "composition": [...],
            "inscription": [...],
            "quality": [...],
        }
    """
    from . import (
        layer_subject,
        layer_scene,
        layer_style,
        layer_lighting,
        layer_composition,
        layer_inscription,
        layer_quality,
    )

    layers = {
        "subject": layer_subject.LAYER,
        "scene": layer_scene.LAYER,
        "style": layer_style.LAYER,
        "lighting": layer_lighting.LAYER,
        "composition": layer_composition.LAYER,
        "inscription": layer_inscription.LAYER,
        "quality": layer_quality.LAYER,
    }
    return layers


def get_layer_info() -> Dict[str, int]:
    """返回各层选项数量。"""
    layers = load_all_layers()
    return {k: len(v) for k, v in layers.items()}


__all__ = [
    "LAYER_ORDER",
    "LAYER_NAMES_CN",
    "LAYER_PRIORITY",
    "load_all_layers",
    "get_layer_info",
]