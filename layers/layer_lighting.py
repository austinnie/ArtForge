# layers/layer_lighting.py
"""
第 4 层：光影

包含：
  - 时间光影（晨、午、黄昏、夜、黎明）
  - 光源（月、烛、灯笼、雪光、火）
  - 天气光（雾、雨、雪、晴、阴）
  - 氛围光（柔、硬、暖、冷、明暗对比）

格式：英文 prompt 短语（逗号分隔）
"""

LAYER = [
    # ==================== 时间光影 ====================
    "soft morning light filtering through mist, "
    "pale golden tones, gentle shadow transitions",

    "bright midday sun, crisp shadows, "
    "high contrast, clear colors",

    "golden hour light, warm amber glow, "
    "long soft shadows, romantic atmosphere",

    "deep twilight, indigo sky, "
    "fading orange on the horizon, quiet mood",

    "moonlight on a clear night, cool silver tones, "
    "crisp shadows, ethereal glow",

    "faint dawn light, pale pink and blue sky, "
    "lingering mist, first birds singing",

    # ==================== 光源 ====================
    "a single oil lamp casting warm circles on tatami, "
    "deep shadows around, intimate atmosphere",

    "a paper lantern glowing softly, "
    "warm golden light, blurring outlines, night scene",

    "reflected candlelight in dark eyes, "
    "tiny flame, intimate mood, chiaroscuro",

    "snow-reflected starlight, "
    "silvery blue tones, faint horizon, quiet cold",

    "a small fire in the dark, "
    "dancing orange glow, sharp shadow edges, dramatic",

    "distant lantern lights across water, "
    "long reflections, blurred edges, melancholic",

    # ==================== 天气光 ====================
    "diffused light through heavy fog, "
    "soft edges, muted colors, mysterious atmosphere",

    "rain falling in slanting light, "
    "bright droplets, wet surfaces, cool tones",

    "sunlight after rain, "
    "rainbow in the distance, glistening leaves",

    "snowfall at dusk, "
    "huge soft flakes, blue-grey tones, silent atmosphere",

    "overcast sky with diffused light, "
    "flat shadows, soft grey palette, contemplative",

    "sunbeams breaking through clouds, "
    "dramatic shafts of light, dust motes, sacred atmosphere",

    # ==================== 氛围光 ====================
    "chiaroscuro contrast, "
    "dramatic light and shadow, hidden details, mysterious",

    "soft flattering light, "
    "gentle gradients, warm mid-tones, elegant",

    "cold blue light with a single warm accent, "
    "dramatic color contrast, cinematic",

    "glowing inner light, self-illuminated subject, "
    "mystical atmosphere, magical glow",

    "backlit silhouette against glowing background, "
    "rim light along edges, iconic pose",

    "high-key lighting, bright and airy, "
    "minimal shadows, delicate beauty",
]