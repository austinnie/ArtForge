# layers/layer_scene.py
"""
第 2 层：场景

包含：
  - 自然（山林、海边、竹林、雪原、花田）
  - 建筑（宫廷、庭院、寺庙、茶室、街道）
  - 室内（卧室、书房、温泉、屏风前）
  - 季节（春樱、夏荷、秋枫、冬雪）
  - 天气（雨、雾、雪、晴、黄昏）

格式：英文 prompt 短语（逗号分隔）
"""

LAYER = [
    # ==================== 自然 ====================
    "a deep mountain forest at dawn, misty peaks, "
    "ancient cedar trees, shafts of morning light",

    "a rocky mountain path in autumn, "
    "bright red maple leaves falling, distant peaks in haze",

    "a tranquil lake reflecting the full moon, "
    "reeds along the shore, faint mist over the water",

    "a bamboo grove in soft rain, "
    "vertical green stalks, dripping leaves, quiet atmosphere",

    "a snow-covered pine forest at dusk, "
    "long blue shadows, a single figure walking away",

    "a windswept grassy plain at sunset, "
    "endless horizon, warm golden light, solitary tree",

    "a plum grove in early spring, "
    "bare branches with the first pink blossoms, light snow",

    "a rocky stream winding through moss-covered stones, "
    "clear water, autumn leaves drifting",

    # ==================== 建筑 / 庭院 ====================
    "a shinden-zukuri Heian palace, "
    "wooden veranda, pond garden, weeping willows, refined",

    "a quiet Zen rock garden, "
    "raked white gravel, moss-covered stones, minimal",

    "a traditional Japanese tea house in a garden, "
    "thatched roof, stepping stones, moss, quiet solitude",

    "an ancient temple on a mountain, "
    "stone steps, red torii gates, mist between cedars",

    "a red-lacquered gate at dusk, "
    "stone lanterns flickering, cherry petals falling",

    "an Edo-period street at night, "
    "wooden shop fronts, paper lanterns, wet stone pavement",

    "a Chinese scholar's garden, "
    "moon gate, rockery, lotus pond, covered walkway",

    "a Tang dynasty palace courtyard, "
    "red pillars, golden roof tiles, peonies in bloom",

    # ==================== 室内 ====================
    "an Edo-period bedroom at night, "
    "paper sliding screens, a single candle, tatami floor",

    "a Heian court lady's chamber, "
    "layered silk curtains, incense burner, evening light",

    "a scholar's study with a low desk, "
    "ink stone, brush, rolled scrolls, soft window light",

    "a hot spring open-air bath, "
    "steaming water, snow falling, wooden rocks, moon above",

    "a tea room interior, "
    "tatami floor, flower arrangement, iron kettle, minimal",

    # ==================== 季节性 ====================
    "a cherry blossom avenue in full bloom, "
    "petals drifting like snow, pale pink light everywhere",

    "a lotus pond in high summer, "
    "large round leaves, pink blossoms opening, dragonflies",

    "a maple valley in late autumn, "
    "brilliant red and orange leaves reflected in a river",

    "a snow-covered village in deep winter, "
    "thatched roofs, smoke from chimneys, quiet stillness",

    # ==================== 天气 / 光影氛围 ====================
    "a misty morning with low fog over rice fields, "
    "a faint red sun rising, farmers in the distance",

    "light rain on a forest path, "
    "sunbeams breaking through wet leaves, one lantern",

    "a thunderstorm over a mountain, "
    "dark clouds, flashes of lightning, silhouetted trees",

    "a golden hour over a coastal cliff, "
    "warm light, long shadows, waves crashing below",

    "a moonless night sky with the Milky Way, "
    "silhouetted pine trees, faint reflection in a lake",
]