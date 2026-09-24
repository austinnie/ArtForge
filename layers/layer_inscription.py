# layers/layer_inscription.py
"""
第 6 层：题词印章

包含：
  - 题词位置与形式（顶部题诗、右侧落款、角落款识）
  - 书法风格（行书、楷书、草书、篆书）
  - 印章形式（朱文印、白文印、多方印）
  - 年代感（做旧、泛黄、墨韵）

格式：英文 prompt 短语（逗号分隔）
"""

LAYER = [
    # ==================== 题词形式 ====================
    "vertical Chinese calligraphy poem at the top, "
    "elegant brush strokes, red seal below",

    "vertical Japanese waka calligraphy on the right side, "
    "flowing kana, subtle ink gradation",

    "short haiku inscribed in the upper right corner, "
    "fine cursive brushwork, tiny red seal nearby",

    "a colophon at the bottom left, "
    "small regular-script characters, dated signature",

    "artist's signature and date at the lower left, "
    "paired seals, refined scholarly style",

    "an inscription across the top edge, "
    "single-line poem, generous negative space below",

    # ==================== 书法风格 ====================
    "flowing cursive calligraphy, "
    "spontaneous brush strokes, ink splashes",

    "formal regular-script calligraphy, "
    "clear balanced characters, scholarly dignity",

    "semi-cursive running script, "
    "smooth connections, natural rhythm",

    "seal-script characters in a square seal, "
    "ancient style, vermilion red, dense texture",

    # ==================== 印章 ====================
    "one small red seal at the bottom left, "
    "zhu-wen relief style, minimal",

    "two paired red seals near the signature, "
    "one zhu-wen one bai-wen, balanced composition",

    "a large bai-wen seal at the bottom right, "
    "white characters on vermilion ground, "
    "yin-style, prominent",

    "multiple seals scattered along the edges, "
    "collectors' seals, aged impressions",

    # ==================== 年代感 ====================
    "on aged xuan paper with subtle yellowing, "
    "fine foxing spots, gentle edge wear",

    "on silk with soft creases and fading, "
    "patina of centuries, quiet dignity",

    "ink slightly bleeding into the paper, "
    "halo around strokes, handmade paper texture",

    "edge wear, torn corners, "
    "antique scroll mounting with silk borders",

    "overall patina, warm brown tones, "
    "signs of age and careful preservation",
]