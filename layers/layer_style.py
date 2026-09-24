# layers/layer_style.py
"""
第 3 层：画风

本层直接引用 config.art_config 中的画风定义，
保证与配置层完全同步，避免重复维护。

支持的分类：
  - japanese  日本画风
  - gufeng    古风画风
  - tang      唐风画风
  - genji     源氏物语（场景作为风格使用）
  - art_nude  艺术裸体（骨架）

导出：
  LAYER        所有画风短语的扁平列表（用于通用组合）
  BY_CATEGORY  按分类分组的字典（用于精细控制）
"""

from config.art_config import (
    JAPANESE_STYLES,
    GUFENG_STYLES,
    TANG_STYLES,
    GENJI_SCENES,
    YOKAI_DICT,
    ART_NUDE_STYLES,
)


def _collect_prompts(styles_dict: dict) -> list:
    """从画风字典里提取所有 prompt，去掉空的。"""
    result = []
    for key, item in styles_dict.items():
        if key.startswith("_"):     # 跳过 _placeholder 之类的内部 key
            continue
        p = item.get("prompt", "").strip()
        if p:
            result.append(p)
    return result


# 各分类的画风短语
JAPANESE_PROMPTS = _collect_prompts(JAPANESE_STYLES)
GUFENG_PROMPTS = _collect_prompts(GUFENG_STYLES)
TANG_PROMPTS = _collect_prompts(TANG_STYLES)
GENJI_PROMPTS = _collect_prompts(GENJI_SCENES)
YOKAI_PROMPTS = _collect_prompts(YOKAI_DICT)
ART_NUDE_PROMPTS = _collect_prompts(ART_NUDE_STYLES)


# 扁平列表（通用组合时用）
LAYER = (
    JAPANESE_PROMPTS
    + GUFENG_PROMPTS
    + TANG_PROMPTS
    + GENJI_PROMPTS
    + ART_NUDE_PROMPTS
)


# 按分类分组（精细控制时用）
BY_CATEGORY = {
    "japanese": JAPANESE_PROMPTS,
    "gufeng": GUFENG_PROMPTS,
    "tang": TANG_PROMPTS,
    "genji": GENJI_PROMPTS,
    "art_nude": ART_NUDE_PROMPTS,
}


def get_by_category(category: str) -> list:
    """获取某分类下的画风短语列表。"""
    return BY_CATEGORY.get(category, [])