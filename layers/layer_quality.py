# layers/layer_quality.py
"""
第 7 层：画质

包含：
  - 品质词（masterpiece、best quality）
  - 细节（highly detailed、intricate）
  - 分辨率（8k、uhd）
  - 风格锐度（sharp focus、crisp）
  - 艺术性（award-winning、museum quality）

格式：英文 prompt 短语（逗号分隔）
"""

LAYER = [
    # ==================== 通用品质 ====================
    "masterpiece, best quality, highly detailed",

    "masterpiece, best quality, ultra detailed, sharp focus",

    "award-winning artwork, museum quality, "
    "exquisite detail, perfect composition",

    # ==================== 分辨率 / 细节 ====================
    "8k uhd, extremely detailed, "
    "intricate brushwork, subtle texture",

    "4k, high resolution, "
    "crisp edges, refined detail everywhere",

    "ultra-detailed, "
    "every brushstroke visible, delicate linework",

    # ==================== 风格专属 ====================
    "traditional East Asian brushwork, "
    "elegant composition, harmonious colors",

    "refined ukiyo-e print quality, "
    "crisp outlines, flat vibrant colors, woodblock grain",

    "traditional ink painting quality, "
    "subtle wash gradations, perfect paper texture",

    "museum-quality antique scroll, "
    "authentic patina, masterful craftsmanship",

    # ==================== 光影 / 氛围 ====================
    "cinematic lighting, dramatic mood, "
    "perfect tonal balance",

    "soft atmospheric lighting, "
    "gentle gradients, painterly mood",

    "poetic atmosphere, contemplative mood, "
    "visual harmony, timeless beauty",

    # ==================== 精简（可选，适合负面/短提示） ====================
    "beautiful composition, fine detail",

    "elegant, refined, graceful",

    "timeless, classic, refined aesthetic",
]