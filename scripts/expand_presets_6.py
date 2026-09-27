# scripts/expand_presets_6.py
"""
第六批：花道、茶道、香道、星象、梦境、战争、音乐家、舞蹈
共 8 类 48 个预设
"""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PRESETS_DIR = PROJECT_ROOT / "presets"


def make_preset(category, name, theme, subject, scene, style, lighting,
                composition, quality):
    def fmt(lst):
        items = ",\n".join(f'            "{x}"' for x in lst)
        return f"[\n{items},\n        ]"

    return f'''# presets/{category}/{name}.py
"""{theme} - {category}"""

PRESET = {{
    "name": "{theme}",
    "category": "{category}",
    "theme": "{theme}",
    "layers": {{
        "subject": {fmt(subject)},
        "scene": {fmt(scene)},
        "style": {fmt(style)},
        "lighting": {fmt(lighting)},
        "composition": {fmt(composition)},
        "quality": {fmt(quality)},
    }},
}}
'''


PRESETS = {

    # ============================================================
    # 花道
    # ============================================================
    "flower_arrangement": {
        "ikenobo": {
            "theme": "池坊",
            "subject": [
                "an Ikenobo ikebana arrangement, "
                "standing style rikka, "
                "pine branch and chrysanthemum",
                "an Ikenobo master arranging flowers, "
                "with scissors and kenzan, "
                "in a studio",
                "an Ikenobo shoka arrangement, "
                "heaven, earth and human lines, "
                "seasonal flowers",
            ],
            "scene": [
                "tokonoma alcove, "
                "hanging scroll, "
                "tatami room",
                "flower studio, "
                "bamboo blinds, "
                "morning light",
                "temple hall, "
                "incense, "
                "wooden pillars",
            ],
            "style": [
                "traditional Japanese ikebana painting, "
                "nihonga, refined brushwork",
                "gongbi details, precise botanical forms",
                "in the style of Ikenobo school",
            ],
            "lighting": [
                "soft morning light",
                "afternoon, dappled",
                "moonlight, silver",
            ],
            "composition": [
                "vertical hanging scroll, kakemono",
                "square album leaf",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Ikenobo ikebana painting",
                "8k uhd, refined elegance",
            ],
        },
        "ohara": {
            "theme": "小原流",
            "subject": [
                "an Ohara school ikebana, "
                "landscape arrangement, "
                "pine and stones",
                "an Ohara ikebana in a shallow bowl, "
                "water surface, "
                "seasonal branches",
                "an Ohara master arranging, "
                "with kenzan, "
                "in a bright studio",
            ],
            "scene": [
                "bright studio, "
                "white walls, "
                "large window",
                "garden room, "
                "stone basin, "
                "bamboo",
                "exhibition hall, "
                "spotlight, "
                "shallow bowl",
            ],
            "style": [
                "modern Japanese ikebana painting, "
                "nihonga, naturalistic",
                "gongbi details, soft washes",
                "in the style of Ohara school",
            ],
            "lighting": [
                "bright natural light",
                "afternoon, warm",
                "soft studio light",
            ],
            "composition": [
                "horizontal panel",
                "square album leaf",
                "vertical hanging scroll, kakemono",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Ohara ikebana painting",
                "8k uhd, natural elegance",
            ],
        },
        "sogetsu": {
            "theme": "草月",
            "subject": [
                "a Sogetsu ikebana, "
                "free style, "
                "bold sculptural forms",
                "a Sogetsu arrangement, "
                "with metal and driftwood, "
                "modern",
                "a Sogetsu master, "
                "creating an installation, "
                "large scale",
            ],
            "scene": [
                "modern gallery, "
                "white space, "
                "concrete",
                "loft studio, "
                "large windows, "
                "metal",
                "outdoor plaza, "
                "sculpture, "
                "sky",
            ],
            "style": [
                "modern Japanese ikebana, "
                "bold sculptural, minimal",
                "contemporary art photography style",
                "in the style of Sogetsu school",
            ],
            "lighting": [
                "dramatic spotlight",
                "cool studio light",
                "natural light, modern",
            ],
            "composition": [
                "vertical panel",
                "square format",
                "horizontal panel",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Sogetsu ikebana",
                "8k uhd, sculptural elegance",
            ],
        },
        "nageire": {
            "theme": "投入",
            "subject": [
                "a nageire arrangement, "
                "in a tall vase, "
                "casual thrown-in style",
                "a nageire ikebana, "
                "with branches and flowers, "
                "natural",
                "a tea room nageire, "
                "simple, "
                "seasonal",
            ],
            "scene": [
                "tea room, "
                "tokonoma, "
                "tatami",
                "rustic studio, "
                "clay vase, "
                "bamboo",
                "mountain hut, "
                "wooden beam, "
                "window",
            ],
            "style": [
                "traditional Japanese ikebana painting, "
                "wabi-sabi, "
                "ink and wash",
                "in the style of tea ceremony aesthetics",
                "gongbi details, natural forms",
            ],
            "lighting": [
                "soft dim light",
                "candlelight, warm",
                "morning light, gentle",
            ],
            "composition": [
                "vertical hanging scroll, kakemono",
                "square album leaf",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "nageire ikebana painting",
                "8k uhd, wabi-sabi elegance",
            ],
        },
        "rikka": {
            "theme": "立华",
            "subject": [
                "a rikka ikebana, "
                "tall standing style, "
                "pine and peony",
                "a rikka arrangement, "
                "with nine main branches, "
                "formal",
                "a rikka master, "
                "in ceremonial dress, "
                "arranging",
            ],
            "scene": [
                "temple hall, "
                "golden Buddha, "
                "incense",
                "formal alcove, "
                "hanging scroll, "
                "bronze vase",
                "ceremonial room, "
                "tatami, "
                "screen",
            ],
            "style": [
                "traditional Japanese rikka painting, "
                "nihonga, precise",
                "gongbi details, mineral pigments",
                "in the style of Ikenobo rikka",
            ],
            "lighting": [
                "solemn temple light",
                "candlelight, warm",
                "daylight, formal",
            ],
            "composition": [
                "vertical hanging scroll, kakemono",
                "square album leaf",
                "horizontal handscroll",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "rikka ikebana painting",
                "8k uhd, formal grandeur",
            ],
        },
        "shoka": {
            "theme": "生花",
            "subject": [
                "a shoka ikebana, "
                "heaven earth human lines, "
                "seasonal flower",
                "a shoka arrangement, "
                "with one main flower, "
                "minimal",
                "a shoka master, "
                "teaching, "
                "with students",
            ],
            "scene": [
                "tatami room, "
                "tokonoma, "
                "hanging scroll",
                "studio, "
                "bamboo blinds, "
                "morning",
                "exhibition, "
                "spotlight, "
                "vase",
            ],
            "style": [
                "traditional Japanese ikebana painting, "
                "nihonga, delicate",
                "gongbi details, precise",
                "in the style of Ikenobo shoka",
            ],
            "lighting": [
                "soft morning light",
                "afternoon, warm",
                "moonlight, silver",
            ],
            "composition": [
                "vertical hanging scroll, kakemono",
                "square album leaf",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "shoka ikebana painting",
                "8k uhd, refined simplicity",
            ],
        },
    },

    # ============================================================
    # 茶道
    # ============================================================
    "tea_ceremony": {
        "sencha": {
            "theme": "煎茶",
            "subject": [
                "a sencha tea ceremony, "
                "teapot and cups, "
                "steeping leaves",
                "a sencha master, "
                "pouring tea, "
                "with a kyusu",
                "a sencha tea table, "
                "with sweets, "
                "seasonal flowers",
            ],
            "scene": [
                "tea room, "
                "tatami, "
                "bamboo blinds",
                "garden veranda, "
                "pine, "
                "stone lantern",
                "studio, "
                "tea utensils, "
                "scroll",
            ],
            "style": [
                "Japanese sencha tea painting, "
                "nihonga, refined",
                "gongbi details, soft washes",
                "in the style of literati tea painting",
            ],
            "lighting": [
                "soft daylight",
                "afternoon, warm",
                "morning light, fresh",
            ],
            "composition": [
                "horizontal handscroll",
                "square album leaf",
                "vertical hanging scroll, kakemono",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "sencha tea ceremony painting",
                "8k uhd, refined elegance",
            ],
        },
        "matcha": {
            "theme": "抹茶",
            "subject": [
                "a matcha tea ceremony, "
                "whisking tea, "
                "chawan bowl",
                "a tea master, "
                "in kimono, "
                "whisking matcha",
                "a matcha tea setting, "
                "with chasen and chashaku, "
                "tatami",
            ],
            "scene": [
                "tea room, "
                "tatami, "
                "tokonoma",
                "temple, "
                "incense, "
                "wooden pillars",
                "garden tea house, "
                "stone basin, "
                "bamboo",
            ],
            "style": [
                "Japanese matcha tea painting, "
                "nihonga, wabi-sabi",
                "gongbi details, soft green tones",
                "in the style of tea ceremony aesthetics",
            ],
            "lighting": [
                "soft dim light",
                "morning light, gentle",
                "candlelight, warm",
            ],
            "composition": [
                "square album leaf",
                "vertical hanging scroll, kakemono",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "matcha tea ceremony painting",
                "8k uhd, wabi-sabi elegance",
            ],
        },
        "gongfu": {
            "theme": "工夫茶",
            "subject": [
                "a gongfu tea ceremony, "
                "small teapot and cups, "
                "oolong tea",
                "a gongfu tea master, "
                "pouring tea, "
                "with a gaiwan",
                "a gongfu tea table, "
                "with tea pet, "
                "bamboo tray",
            ],
            "scene": [
                "Chinese tea house, "
                "wooden table, "
                "bamboo",
                "scholar's studio, "
                "tea utensils, "
                "scroll",
                "courtyard, "
                "stone table, "
                "pine",
            ],
            "style": [
                "Chinese gongfu tea painting, "
                "gongbi details, refined",
                "literati painting, xieyi freehand",
                "in the style of Ming dynasty tea painting",
            ],
            "lighting": [
                "soft interior light",
                "afternoon, warm",
                "moonlight, silver",
            ],
            "composition": [
                "horizontal handscroll",
                "square album leaf",
                "vertical hanging scroll, lidu",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "gongfu tea ceremony painting",
                "8k uhd, refined elegance",
            ],
        },
        "zen_tea": {
            "theme": "禅茶",
            "subject": [
                "a Zen tea ceremony, "
                "monk whisking tea, "
                "minimal",
                "a Zen tea bowl, "
                "with tea whisk, "
                "on a rock",
                "a Zen tea master, "
                "in meditation, "
                "with tea",
            ],
            "scene": [
                "Zen temple, "
                "stone garden, "
                "moss",
                "mountain hut, "
                "tea kettle, "
                "steam",
                "empty room, "
                "cushion, "
                "incense",
            ],
            "style": [
                "Chinese Chan painting, "
                "in the style of Liang Kai",
                "ink and wash, xieyi, "
                "minimal brushwork",
                "literati painting, vast negative space",
            ],
            "lighting": [
                "soft misty light",
                "moonlight, silver",
                "soft daylight, minimal",
            ],
            "composition": [
                "square album leaf",
                "vertical hanging scroll, lidu",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Zen tea painting",
                "8k uhd, zen simplicity",
            ],
        },
        "literati_tea": {
            "theme": "文人茶",
            "subject": [
                "a literati tea gathering, "
                "scholars tasting tea, "
                "poetry and tea",
                "a scholar brewing tea, "
                "with a bamboo stove, "
                "in a studio",
                "a literati tea table, "
                "with books and tea, "
                "ink stone",
            ],
            "scene": [
                "scholar's studio, "
                "books, "
                "ink stone",
                "garden pavilion, "
                "bamboo, "
                "lotus pond",
                "mountain retreat, "
                "pine, "
                "stream",
            ],
            "style": [
                "Chinese literati painting, "
                "gongbi details, refined",
                "in the style of Wen Zhengming",
                "literati painting, xieyi freehand",
            ],
            "lighting": [
                "soft interior light",
                "afternoon, dappled",
                "moonlight, silver",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "literati tea painting",
                "8k uhd, scholarly elegance",
            ],
        },
        "tea_contest": {
            "theme": "斗茶",
            "subject": [
                "a Song dynasty tea contest, "
                "whisking tea, "
                "comparing foam",
                "a tea contest scene, "
                "with tea bowls, "
                "scholars watching",
                "a tea master, "
                "whisking tea, "
                "with a crowd",
            ],
            "scene": [
                "Song dynasty tea house, "
                "wooden tables, "
                "lanterns",
                "courtyard, "
                "tea tables, "
                "bamboo",
                "market street, "
                "tea stalls, "
                "crowd",
            ],
            "style": [
                "Song dynasty tea painting, "
                "gongbi details, precise",
                "in the style of Song dynasty genre painting",
                "literati painting, xieyi freehand",
            ],
            "lighting": [
                "daylight, warm",
                "lantern light, warm",
                "afternoon, bright",
            ],
            "composition": [
                "horizontal handscroll",
                "square album leaf",
                "vertical hanging scroll, lidu",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Song dynasty tea contest painting",
                "8k uhd, lively elegance",
            ],
        },
    },

    # ============================================================
    # 香道
    # ============================================================
    "incense": {
        "incense_ceremony": {
            "theme": "香席",
            "subject": [
                "a Japanese incense ceremony, "
                "kodo, "
                "listening to incense",
                "a kodo master, "
                "with incense utensils, "
                "in a tatami room",
                "an incense ceremony, "
                "with guests, "
                "incense burner",
            ],
            "scene": [
                "tatami room, "
                "tokonoma, "
                "incense",
                "temple hall, "
                "wooden pillars, "
                "lamps",
                "tea room, "
                "bamboo blinds, "
                "morning",
            ],
            "style": [
                "Japanese incense ceremony painting, "
                "nihonga, refined",
                "gongbi details, soft washes",
                "in the style of kodo aesthetics",
            ],
            "lighting": [
                "soft dim light",
                "candlelight, warm",
                "morning light, gentle",
            ],
            "composition": [
                "vertical hanging scroll, kakemono",
                "square album leaf",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "incense ceremony painting",
                "8k uhd, refined elegance",
            ],
        },
        "incense_utensils": {
            "theme": "香具",
            "subject": [
                "incense utensils, "
                "incense burner, "
                "incense box, "
                "tools",
                "a set of incense tools, "
                "with mica plate, "
                "on a tray",
                "an incense burner, "
                "with smoke rising, "
                "on a stand",
            ],
            "scene": [
                "scholar's studio, "
                "incense, "
                "books",
                "tea room, "
                "tatami, "
                "incense",
                "temple, "
                "altar, "
                "lamps",
            ],
            "style": [
                "Chinese gongbi still life, "
                "precise details, "
                "mineral pigments",
                "Ming dynasty painting",
                "imperial collection style",
            ],
            "lighting": [
                "soft interior light",
                "candlelight, warm",
                "daylight, jewel glow",
            ],
            "composition": [
                "square album leaf",
                "vertical hanging scroll, lidu",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "incense utensils painting",
                "8k uhd, refined elegance",
            ],
        },
        "incense_wood": {
            "theme": "香木",
            "subject": [
                "precious incense wood, "
                "agarwood, sandalwood, "
                "on a tray",
                "a piece of agarwood, "
                "with intricate grain, "
                "on silk",
                "incense wood chips, "
                "in a bowl, "
                "with tools",
            ],
            "scene": [
                "scholar's studio, "
                "incense, "
                "books",
                "apothecary, "
                "herb drawers, "
                "balance scale",
                "temple, "
                "altar, "
                "lamps",
            ],
            "style": [
                "Chinese gongbi still life, "
                "precise botanical details",
                "Ming dynasty pharmacopoeia illustration",
                "literati painting, xieyi freehand",
            ],
            "lighting": [
                "soft daylight",
                "afternoon, warm",
                "morning light, fresh",
            ],
            "composition": [
                "square album leaf",
                "vertical hanging scroll, lidu",
                "horizontal handscroll",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "incense wood painting",
                "8k uhd, botanical precision",
            ],
        },
        "blended_incense": {
            "theme": "合香",
            "subject": [
                "a Taoist alchemist, "
                "blending incense, "
                "with mortar and pestle",
                "a scholar blending incense, "
                "with recipe, "
                "in a studio",
                "blended incense, "
                "in a jar, "
                "with tools",
            ],
            "scene": [
                "scholar's studio, "
                "incense, "
                "books",
                "apothecary, "
                "herb drawers, "
                "balance scale",
                "mountain cave, "
                "alchemy, "
                "smoke",
            ],
            "style": [
                "Chinese Taoist painting, "
                "mineral pigments, gold accents",
                "gongbi details, precise",
                "in the style of Ming dynasty painting",
            ],
            "lighting": [
                "cave light, mysterious",
                "candlelight, warm",
                "moonlight, silver",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square album leaf",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "blended incense painting",
                "8k uhd, mystical atmosphere",
            ],
        },
        "incense_appreciation": {
            "theme": "品香",
            "subject": [
                "a scholar appreciating incense, "
                "with incense burner, "
                "in a studio",
                "a group of scholars, "
                "tasting incense, "
                "with incense tools",
                "a lady appreciating incense, "
                "with incense burner, "
                "in a garden",
            ],
            "scene": [
                "scholar's studio, "
                "books, "
                "incense",
                "garden pavilion, "
                "bamboo, "
                "incense",
                "tea room, "
                "tatami, "
                "incense",
            ],
            "style": [
                "Chinese gongbi painting, "
                "precise details, "
                "in the style of Ming dynasty illustration",
                "literati painting, xieyi freehand",
                "Ming dynasty genre painting",
            ],
            "lighting": [
                "soft interior light",
                "candlelight, warm",
                "daylight, natural",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "incense appreciation painting",
                "8k uhd, refined elegance",
            ],
        },
        "incense_gathering": {
            "theme": "香会",
            "subject": [
                "an incense gathering, "
                "scholars and ladies, "
                "incense and poetry",
                "a large incense ceremony, "
                "with many guests, "
                "incense burners",
                "a temple incense festival, "
                "with pilgrims, "
                "incense smoke",
            ],
            "scene": [
                "garden pavilion, "
                "incense, "
                "poetry",
                "temple, "
                "incense, "
                "crowd",
                "court, "
                "incense, "
                "banquet",
            ],
            "style": [
                "Chinese gongbi painting, "
                "precise details, "
                "in the style of Ming dynasty illustration",
                "literati painting, xieyi freehand",
                "Ming dynasty genre painting",
            ],
            "lighting": [
                "daylight, warm",
                "lantern light, warm",
                "incense glow, mystical",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "incense gathering painting",
                "8k uhd, lively elegance",
            ],
        },
    },

    # ============================================================
    # 星象
    # ============================================================
    "astrology": {
        "twenty_eight_mansions": {
            "theme": "二十八宿",
            "subject": [
                "the twenty-eight lunar mansions, "
                "with star deities, "
                "in the sky",
                "a star map of the twenty-eight mansions, "
                "with Chinese constellations",
                "a Taoist star deity, "
                "with constellation patterns, "
                "in the clouds",
            ],
            "scene": [
                "night sky, "
                "stars, "
                "clouds",
                "celestial palace, "
                "jade terraces, "
                "stars",
                "mountain peak, "
                "observatory, "
                "night",
            ],
            "style": [
                "traditional Chinese star painting, "
                "mineral pigments, gold accents",
                "Dunhuang mural style",
                "in the style of Han dynasty star map",
            ],
            "lighting": [
                "starlight, silver",
                "moonlight, silver",
                "celestial glow",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square mural",
                "horizontal handscroll",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese star painting",
                "8k uhd, celestial radiance",
            ],
        },
        "big_dipper": {
            "theme": "北斗",
            "subject": [
                "the Big Dipper, "
                "seven stars, "
                "in the night sky",
                "a Taoist priest, "
                "worshipping the Big Dipper, "
                "with incense",
                "the Big Dipper, "
                "with star deities, "
                "in the clouds",
            ],
            "scene": [
                "night sky, "
                "stars, "
                "mountains",
                "Taoist temple, "
                "altar, "
                "incense",
                "celestial palace, "
                "jade terraces, "
                "stars",
            ],
            "style": [
                "traditional Chinese star painting, "
                "mineral pigments, gold accents",
                "Dunhuang mural style",
                "in the style of Taoist star map",
            ],
            "lighting": [
                "starlight, silver",
                "moonlight, silver",
                "celestial glow",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square mural",
                "horizontal handscroll",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Big Dipper painting",
                "8k uhd, celestial radiance",
            ],
        },
        "milky_way": {
            "theme": "银河",
            "subject": [
                "the Milky Way, "
                "with stars and clouds, "
                "in the night sky",
                "a celestial river, "
                "with stars, "
                "in the sky",
                "the Milky Way, "
                "with star deities, "
                "in the clouds",
            ],
            "scene": [
                "night sky, "
                "stars, "
                "clouds",
                "celestial river, "
                "jade terraces, "
                "stars",
                "mountain peak, "
                "observatory, "
                "night",
            ],
            "style": [
                "traditional Chinese star painting, "
                "mineral pigments, gold accents",
                "Dunhuang mural style",
                "in the style of Han dynasty star map",
            ],
            "lighting": [
                "starlight, silver",
                "moonlight, silver",
                "celestial glow",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square mural",
                "horizontal handscroll",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Milky Way painting",
                "8k uhd, celestial radiance",
            ],
        },
        "sun_moon": {
            "theme": "日月",
            "subject": [
                "the sun and moon, "
                "with star deities, "
                "in the sky",
                "a sun bird and moon rabbit, "
                "with constellations, "
                "in the sky",
                "the sun and moon, "
                "with Taoist deities, "
                "in the clouds",
            ],
            "scene": [
                "sky, "
                "sun, "
                "moon",
                "celestial palace, "
                "jade terraces, "
                "stars",
                "mountain peak, "
                "observatory, "
                "day and night",
            ],
            "style": [
                "traditional Chinese star painting, "
                "mineral pigments, gold accents",
                "Dunhuang mural style",
                "in the style of Han dynasty star map",
            ],
            "lighting": [
                "sunlight and moonlight",
                "celestial glow",
                "dawn light",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square mural",
                "horizontal handscroll",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "sun and moon painting",
                "8k uhd, celestial radiance",
            ],
        },
        "star_officials": {
            "theme": "星官",
            "subject": [
                "Chinese star officials, "
                "with constellation patterns, "
                "in the sky",
                "a star official, "
                "with a star map, "
                "in the clouds",
                "a group of star officials, "
                "with constellations, "
                "in the sky",
            ],
            "scene": [
                "night sky, "
                "stars, "
                "clouds",
                "celestial palace, "
                "jade terraces, "
                "stars",
                "mountain peak, "
                "observatory, "
                "night",
            ],
            "style": [
                "traditional Chinese star painting, "
                "mineral pigments, gold accents",
                "Dunhuang mural style",
                "in the style of Han dynasty star map",
            ],
            "lighting": [
                "starlight, silver",
                "moonlight, silver",
                "celestial glow",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square mural",
                "horizontal handscroll",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese star official painting",
                "8k uhd, celestial radiance",
            ],
        },
        "celestial_phenomena": {
            "theme": "天象",
            "subject": [
                "celestial phenomena, "
                "comets, "
                "eclipses, "
                "auroras",
                "a Chinese astronomer, "
                "observing the sky, "
                "with instruments",
                "celestial phenomena, "
                "with star deities, "
                "in the sky",
            ],
            "scene": [
                "night sky, "
                "stars, "
                "clouds",
                "observatory, "
                "instruments, "
                "night",
                "mountain peak, "
                "observatory, "
                "night",
            ],
            "style": [
                "traditional Chinese star painting, "
                "mineral pigments, gold accents",
                "Dunhuang mural style",
                "in the style of Han dynasty star map",
            ],
            "lighting": [
                "starlight, silver",
                "moonlight, silver",
                "celestial glow",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square mural",
                "horizontal handscroll",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "celestial phenomena painting",
                "8k uhd, celestial radiance",
            ],
        },
    },

    # ============================================================
    # 梦境
    # ============================================================
    "dream": {
        "zhuangzi_butterfly": {
            "theme": "庄周梦蝶",
            "subject": [
                "Zhuangzi dreaming of a butterfly, "
                "with butterflies, "
                "in a garden",
                "a scholar sleeping, "
                "with a butterfly, "
                "in a bamboo grove",
                "a butterfly, "
                "with a dreamy landscape, "
                "in the sky",
            ],
            "scene": [
                "bamboo grove, "
                "butterflies, "
                "mist",
                "garden, "
                "peonies, "
                "butterflies",
                "mountain valley, "
                "clouds, "
                "butterflies",
            ],
            "style": [
                "Chinese ink wash painting, "
                "in the style of Liang Kai",
                "literati painting, xieyi freehand",
                "dreamlike landscape, misty",
            ],
            "lighting": [
                "soft misty light",
                "moonlight, silver",
                "dawn light, dreamy",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Zhuangzi butterfly dream painting",
                "8k uhd, dreamlike elegance",
            ],
        },
        "yellow_millet": {
            "theme": "黄粱一梦",
            "subject": [
                "a scholar dreaming, "
                "with millet cooking, "
                "in an inn",
                "a scholar in a dream, "
                "with a grand palace, "
                "in the clouds",
                "a scholar waking, "
                "with millet, "
                "in an inn",
            ],
            "scene": [
                "inn, "
                "millet, "
                "candle",
                "dream palace, "
                "jade terraces, "
                "clouds",
                "mountain valley, "
                "clouds, "
                "mist",
            ],
            "style": [
                "Chinese ink wash painting, "
                "in the style of Liang Kai",
                "literati painting, xieyi freehand",
                "dreamlike landscape, misty",
            ],
            "lighting": [
                "candlelight, warm",
                "moonlight, silver",
                "dawn light, dreamy",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "yellow millet dream painting",
                "8k uhd, dreamlike elegance",
            ],
        },
        "south_branch": {
            "theme": "南柯一梦",
            "subject": [
                "a scholar dreaming, "
                "with an ant kingdom, "
                "in a garden",
                "a scholar in a dream, "
                "with a grand palace, "
                "in the clouds",
                "a scholar waking, "
                "with ants, "
                "in a garden",
            ],
            "scene": [
                "garden, "
                "ants, "
                "candle",
                "dream palace, "
                "jade terraces, "
                "clouds",
                "mountain valley, "
                "clouds, "
                "mist",
            ],
            "style": [
                "Chinese ink wash painting, "
                "in the style of Liang Kai",
                "literati painting, xieyi freehand",
                "dreamlike landscape, misty",
            ],
            "lighting": [
                "candlelight, warm",
                "moonlight, silver",
                "dawn light, dreamy",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "south branch dream painting",
                "8k uhd, dreamlike elegance",
            ],
        },
        "liaozhai": {
            "theme": "聊斋",
            "subject": [
                "a scholar and a fox spirit, "
                "in a garden, "
                "moonlight",
                "a fox spirit, "
                "with flowing robes, "
                "in a bamboo grove",
                "a ghostly lady, "
                "with a lantern, "
                "in a ruined temple",
            ],
            "scene": [
                "garden, "
                "moon, "
                "fox spirit",
                "bamboo grove, "
                "mist, "
                "ghost",
                "ruined temple, "
                "lantern, "
                "night",
            ],
            "style": [
                "Chinese gongbi painting, "
                "precise details, "
                "in the style of Qing dynasty illustration",
                "literati painting, xieyi freehand",
                "dreamlike landscape, misty",
            ],
            "lighting": [
                "moonlight, silver",
                "lantern light, warm",
                "candlelight, eerie",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Liaozhai painting",
                "8k uhd, ghostly elegance",
            ],
        },
        "illusion": {
            "theme": "幻境",
            "subject": [
                "a dreamlike landscape, "
                "with floating islands, "
                "in the clouds",
                "a scholar, "
                "in a dream, "
                "with a grand palace",
                "a celestial palace, "
                "with jade terraces, "
                "in the clouds",
            ],
            "scene": [
                "cloud sea, "
                "floating islands, "
                "stars",
                "celestial palace, "
                "jade terraces, "
                "clouds",
                "mountain valley, "
                "clouds, "
                "mist",
            ],
            "style": [
                "Chinese ink wash painting, "
                "in the style of Liang Kai",
                "literati painting, xieyi freehand",
                "dreamlike landscape, misty",
            ],
            "lighting": [
                "soft misty light",
                "moonlight, silver",
                "dawn light, dreamy",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "dreamlike landscape painting",
                "8k uhd, dreamlike elegance",
            ],
        },
        "immortal_dream": {
            "theme": "仙梦",
            "subject": [
                "a scholar dreaming, "
                "with an immortal, "
                "in a mountain",
                "an immortal, "
                "with flowing robes, "
                "in the clouds",
                "a scholar in a dream, "
                "with a jade palace, "
                "in the clouds",
            ],
            "scene": [
                "mountain valley, "
                "clouds, "
                "immortal",
                "celestial palace, "
                "jade terraces, "
                "clouds",
                "mountain peak, "
                "clouds, "
                "mist",
            ],
            "style": [
                "Chinese ink wash painting, "
                "in the style of Liang Kai",
                "literati painting, xieyi freehand",
                "dreamlike landscape, misty",
            ],
            "lighting": [
                "soft misty light",
                "moonlight, silver",
                "dawn light, dreamy",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "immortal dream painting",
                "8k uhd, dreamlike elegance",
            ],
        },
    },

    # ============================================================
    # 战争
    # ============================================================
    "war": {
        "siege": {
            "theme": "攻城",
            "subject": [
                "a siege, "
                "soldiers storming a city wall, "
                "ladders and catapults",
                "a siege, "
                "with cavalry and infantry, "
                "city gate",
                "a general, "
                "directing a siege, "
                "with banners",
            ],
            "scene": [
                "city wall, "
                "banners, "
                "smoke",
                "battlefield, "
                "ladders, "
                "fire",
                "mountain pass, "
                "banners, "
                "dramatic sky",
            ],
            "style": [
                "Chinese war painting, "
                "gongbi details, dramatic",
                "in the style of Qing dynasty battle painting",
                "Ming dynasty military illustration",
            ],
            "lighting": [
                "dramatic light",
                "firelight, warm",
                "storm light",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese siege painting",
                "8k uhd, dramatic action",
            ],
        },
        "naval_battle": {
            "theme": "水战",
            "subject": [
                "a naval battle, "
                "warships, "
                "soldiers fighting",
                "a naval battle, "
                "with fire ships, "
                "river",
                "a naval general, "
                "directing a battle, "
                "with flags",
            ],
            "scene": [
                "river, "
                "warships, "
                "smoke",
                "sea, "
                "warships, "
                "fire",
                "lake, "
                "warships, "
                "banners",
            ],
            "style": [
                "Chinese war painting, "
                "gongbi details, dramatic",
                "in the style of Qing dynasty battle painting",
                "Ming dynasty military illustration",
            ],
            "lighting": [
                "dramatic light",
                "firelight, warm",
                "storm light",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese naval battle painting",
                "8k uhd, dramatic action",
            ],
        },
        "cavalry": {
            "theme": "骑兵",
            "subject": [
                "cavalry charging, "
                "horses, "
                "soldiers with spears",
                "a cavalry general, "
                "on horseback, "
                "with a sword",
                "cavalry, "
                "with banners, "
                "steppe",
            ],
            "scene": [
                "steppe, "
                "horses, "
                "banners",
                "battlefield, "
                "cavalry, "
                "smoke",
                "mountain pass, "
                "cavalry, "
                "dramatic sky",
            ],
            "style": [
                "Chinese war painting, "
                "gongbi details, dramatic",
                "in the style of Qing dynasty battle painting",
                "Ming dynasty military illustration",
            ],
            "lighting": [
                "dramatic light",
                "firelight, warm",
                "storm light",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese cavalry painting",
                "8k uhd, dramatic action",
            ],
        },
        "ambush": {
            "theme": "伏击",
            "subject": [
                "an ambush, "
                "soldiers hiding in a forest, "
                "with bows",
                "an ambush, "
                "with cavalry charging, "
                "from the woods",
                "a general, "
                "directing an ambush, "
                "with banners",
            ],
            "scene": [
                "forest, "
                "ambush, "
                "bows",
                "battlefield, "
                "cavalry, "
                "smoke",
                "mountain pass, "
                "ambush, "
                "dramatic sky",
            ],
            "style": [
                "Chinese war painting, "
                "gongbi details, dramatic",
                "in the style of Qing dynasty battle painting",
                "Ming dynasty military illustration",
            ],
            "lighting": [
                "dramatic light",
                "firelight, warm",
                "storm light",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese ambush painting",
                "8k uhd, dramatic action",
            ],
        },
        "military_camp": {
            "theme": "军营",
            "subject": [
                "a military camp, "
                "tents, "
                "soldiers training",
                "a military camp, "
                "with banners, "
                "at night",
                "a general, "
                "in a tent, "
                "with maps",
            ],
            "scene": [
                "camp, "
                "tents, "
                "banners",
                "battlefield, "
                "camp, "
                "campfire",
                "mountain pass, "
                "camp, "
                "night",
            ],
            "style": [
                "Chinese war painting, "
                "gongbi details, dramatic",
                "in the style of Qing dynasty battle painting",
                "Ming dynasty military illustration",
            ],
            "lighting": [
                "dramatic light",
                "campfire, warm",
                "moonlight, silver",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese military camp painting",
                "8k uhd, dramatic atmosphere",
            ],
        },
        "triumph": {
            "theme": "凯旋",
            "subject": [
                "a triumphant army, "
                "with banners, "
                "returning to the city",
                "a general, "
                "on horseback, "
                "with captives",
                "a triumphal parade, "
                "with soldiers, "
                "and cheering crowds",
            ],
            "scene": [
                "city gate, "
                "banners, "
                "crowd",
                "imperial court, "
                "banquet, "
                "lanterns",
                "street, "
                "parade, "
                "festive",
            ],
            "style": [
                "Chinese war painting, "
                "gongbi details, dramatic",
                "in the style of Qing dynasty battle painting",
                "Ming dynasty military illustration",
            ],
            "lighting": [
                "daylight, warm",
                "lantern light, warm",
                "sunset, golden",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese triumph painting",
                "8k uhd, celebratory elegance",
            ],
        },
    },

    # ============================================================
    # 音乐家
    # ============================================================
    "musician": {
        "boya": {
            "theme": "伯牙",
            "subject": [
                "Boya playing the guqin, "
                "with a mountain stream, "
                "pine trees",
                "Boya and Ziqi, "
                "with a guqin, "
                "in a mountain",
                "Boya playing the guqin, "
                "with a waterfall, "
                "mist",
            ],
            "scene": [
                "mountain stream, "
                "pine trees, "
                "mist",
                "waterfall, "
                "cliff, "
                "clouds",
                "mountain retreat, "
                "bamboo, "
                "moon",
            ],
            "style": [
                "Chinese ink wash painting, "
                "in the style of Song dynasty",
                "literati painting, xieyi freehand",
                "gongbi details, refined",
            ],
            "lighting": [
                "soft misty light",
                "moonlight, silver",
                "dawn light, dreamy",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Boya playing guqin painting",
                "8k uhd, refined elegance",
            ],
        },
        "shikuang": {
            "theme": "师旷",
            "subject": [
                "Shi Kuang playing the qin, "
                "with blind eyes, "
                "in a court",
                "Shi Kuang, "
                "with a qin, "
                "in a palace",
                "Shi Kuang playing the qin, "
                "with a ruler listening, "
                "in a hall",
            ],
            "scene": [
                "court, "
                "throne, "
                "lanterns",
                "palace, "
                "screens, "
                "incense",
                "hall, "
                "musicians, "
                "candlelight",
            ],
            "style": [
                "Chinese gongbi painting, "
                "precise details, "
                "in the style of Ming dynasty illustration",
                "literati painting, xieyi freehand",
                "Ming dynasty court painting",
            ],
            "lighting": [
                "candlelight, warm",
                "daylight, formal",
                "imperial radiance, golden",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Shi Kuang painting",
                "8k uhd, refined elegance",
            ],
        },
        "li_guinian": {
            "theme": "李龟年",
            "subject": [
                "Li Guinian, "
                "the Tang musician, "
                "with a flute",
                "Li Guinian, "
                "with a drum, "
                "in a court",
                "Li Guinian, "
                "playing music, "
                "in a garden",
            ],
            "scene": [
                "court, "
                "banquet, "
                "lanterns",
                "palace garden, "
                "peonies, "
                "pavilion",
                "hall, "
                "musicians, "
                "candlelight",
            ],
            "style": [
                "Tang dynasty court painting, "
                "in the style of Zhou Fang",
                "gongbi beauty painting, "
                "fine-line drawing, color washes",
                "Tang dynasty mural style",
            ],
            "lighting": [
                "soft warm daylight",
                "candlelight, intimate",
                "imperial radiance, golden",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Li Guinian painting",
                "8k uhd, refined elegance",
            ],
        },
        "ji_kang": {
            "theme": "嵇康",
            "subject": [
                "Ji Kang playing the guqin, "
                "with flowing robes, "
                "in a bamboo grove",
                "Ji Kang, "
                "with a guqin, "
                "in a mountain",
                "Ji Kang, "
                "playing music, "
                "with a waterfall",
            ],
            "scene": [
                "bamboo grove, "
                "stream, "
                "rocks",
                "mountain retreat, "
                "pine, "
                "clouds",
                "waterfall, "
                "cliff, "
                "moon",
            ],
            "style": [
                "Chinese ink wash painting, "
                "in the style of Wei-Jin dynasty",
                "literati painting, xieyi freehand",
                "gongbi details, refined",
            ],
            "lighting": [
                "soft misty light",
                "moonlight, silver",
                "dawn light, dreamy",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Ji Kang playing guqin painting",
                "8k uhd, refined elegance",
            ],
        },
        "cai_wenji": {
            "theme": "蔡文姬",
            "subject": [
                "Cai Wenji, "
                "the Han poet and musician, "
                "with a harp",
                "Cai Wenji, "
                "with a qin, "
                "in a yurt",
                "Cai Wenji, "
                "playing music, "
                "in a desert camp",
            ],
            "scene": [
                "yurt, "
                "steppe, "
                "snow",
                "desert camp, "
                "horses, "
                "moon",
                "mountain pass, "
                "banners, "
                "dramatic sky",
            ],
            "style": [
                "Han dynasty painting, "
                "mineral pigments, precise details",
                "gongbi figure painting",
                "in the style of Han dynasty fresco",
            ],
            "lighting": [
                "moonlight, silver",
                "campfire, warm",
                "dawn light, dreamy",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Cai Wenji painting",
                "8k uhd, refined elegance",
            ],
        },
        "gongsun_daniang": {
            "theme": "公孙大娘",
            "subject": [
                "Gongsun Daniang, "
                "the Tang dancer, "
                "with a sword",
                "Gongsun Daniang, "
                "dancing with swords, "
                "in a courtyard",
                "Gongsun Daniang, "
                "with flowing robes, "
                "dancing",
            ],
            "scene": [
                "courtyard, "
                "lanterns, "
                "crowd",
                "palace garden, "
                "peonies, "
                "pavilion",
                "hall, "
                "musicians, "
                "candlelight",
            ],
            "style": [
                "Tang dynasty court painting, "
                "in the style of Zhou Fang",
                "gongbi beauty painting, "
                "fine-line drawing, color washes",
                "Tang dynasty mural style",
            ],
            "lighting": [
                "soft warm daylight",
                "candlelight, intimate",
                "lantern light, warm",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Gongsun Daniang painting",
                "8k uhd, refined elegance",
            ],
        },
    },

    # ============================================================
    # 舞蹈
    # ============================================================
    "dance": {
        "nichang": {
            "theme": "霓裳",
            "subject": [
                "a Tang dynasty lady dancing, "
                "in a rainbow-colored robe, "
                "flowing sleeves",
                "a group of dancers, "
                "in rainbow robes, "
                "in a palace",
                "a dancer, "
                "with flowing silk, "
                "in a garden",
            ],
            "scene": [
                "palace hall, "
                "lanterns, "
                "incense",
                "palace garden, "
                "peonies, "
                "pavilion",
                "moon palace, "
                "jade terraces, "
                "clouds",
            ],
            "style": [
                "Tang dynasty court painting, "
                "in the style of Zhou Fang",
                "gongbi beauty painting, "
                "fine-line drawing, color washes",
                "Tang dynasty mural style",
            ],
            "lighting": [
                "soft warm daylight",
                "candlelight, intimate",
                "moonlight, silver",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Tang dynasty dance painting",
                "8k uhd, refined elegance",
            ],
        },
        "huxuan": {
            "theme": "胡旋",
            "subject": [
                "a Tang dynasty lady dancing the huxuan, "
                "spinning, "
                "flowing robes",
                "a group of dancers, "
                "spinning, "
                "in a courtyard",
                "a dancer, "
                "with flowing silk, "
                "in a palace",
            ],
            "scene": [
                "palace hall, "
                "lanterns, "
                "incense",
                "palace garden, "
                "peonies, "
                "pavilion",
                "courtyard, "
                "lanterns, "
                "crowd",
            ],
            "style": [
                "Tang dynasty court painting, "
                "in the style of Zhou Fang",
                "gongbi beauty painting, "
                "fine-line drawing, color washes",
                "Tang dynasty mural style",
            ],
            "lighting": [
                "soft warm daylight",
                "candlelight, intimate",
                "lantern light, warm",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Tang dynasty huxuan dance painting",
                "8k uhd, refined elegance",
            ],
        },
        "sword_dance": {
            "theme": "剑舞",
            "subject": [
                "a sword dance, "
                "with flowing robes, "
                "dramatic pose",
                "a dancer, "
                "with a sword, "
                "in a courtyard",
                "a group of dancers, "
                "with swords, "
                "in a palace",
            ],
            "scene": [
                "courtyard, "
                "lanterns, "
                "crowd",
                "palace garden, "
                "peonies, "
                "pavilion",
                "hall, "
                "musicians, "
                "candlelight",
            ],
            "style": [
                "Tang dynasty court painting, "
                "in the style of Zhou Fang",
                "gongbi beauty painting, "
                "fine-line drawing, color washes",
                "Tang dynasty mural style",
            ],
            "lighting": [
                "soft warm daylight",
                "candlelight, intimate",
                "lantern light, warm",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "sword dance painting",
                "8k uhd, refined elegance",
            ],
        },
        "drum_dance": {
            "theme": "盘鼓",
            "subject": [
                "a drum dance, "
                "with a large drum, "
                "dancers",
                "a group of dancers, "
                "with drums, "
                "in a courtyard",
                "a drummer, "
                "with flowing robes, "
                "dancing",
            ],
            "scene": [
                "courtyard, "
                "lanterns, "
                "crowd",
                "palace garden, "
                "peonies, "
                "pavilion",
                "hall, "
                "musicians, "
                "candlelight",
            ],
            "style": [
                "Tang dynasty court painting, "
                "in the style of Zhou Fang",
                "gongbi beauty painting, "
                "fine-line drawing, color washes",
                "Tang dynasty mural style",
            ],
            "lighting": [
                "soft warm daylight",
                "candlelight, intimate",
                "lantern light, warm",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "drum dance painting",
                "8k uhd, refined elegance",
            ],
        },
        "white_ramie": {
            "theme": "白纻",
            "subject": [
                "a white ramie dance, "
                "with flowing white robes, "
                "dancers",
                "a group of dancers, "
                "in white robes, "
                "in a courtyard",
                "a dancer, "
                "with flowing white silk, "
                "in a palace",
            ],
            "scene": [
                "palace hall, "
                "lanterns, "
                "incense",
                "palace garden, "
                "peonies, "
                "pavilion",
                "courtyard, "
                "lanterns, "
                "crowd",
            ],
            "style": [
                "Tang dynasty court painting, "
                "in the style of Zhou Fang",
                "gongbi beauty painting, "
                "fine-line drawing, color washes",
                "Tang dynasty mural style",
            ],
            "lighting": [
                "soft warm daylight",
                "candlelight, intimate",
                "moonlight, silver",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "white ramie dance painting",
                "8k uhd, refined elegance",
            ],
        },
        "startled_swan": {
            "theme": "惊鸿",
            "subject": [
                "a dancer, "
                "like a startled swan, "
                "flowing robes",
                "a group of dancers, "
                "like swans, "
                "in a palace",
                "a dancer, "
                "with flowing silk, "
                "in a garden",
            ],
            "scene": [
                "palace hall, "
                "lanterns, "
                "incense",
                "palace garden, "
                "peonies, "
                "pavilion",
                "moon palace, "
                "jade terraces, "
                "clouds",
            ],
            "style": [
                "Tang dynasty court painting, "
                "in the style of Zhou Fang",
                "gongbi beauty painting, "
                "fine-line drawing, color washes",
                "Tang dynasty mural style",
            ],
            "lighting": [
                "soft warm daylight",
                "candlelight, intimate",
                "moonlight, silver",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "startled swan dance painting",
                "8k uhd, refined elegance",
            ],
        },
    },
}


def main():
    created = 0
    for category, presets in PRESETS.items():
        cat_dir = PRESETS_DIR / category
        cat_dir.mkdir(parents=True, exist_ok=True)

        init_file = cat_dir / "__init__.py"
        if not init_file.exists():
            init_file.write_text("", encoding="utf-8")

        for preset_name, data in presets.items():
            file_path = cat_dir / f"{preset_name}.py"
            if file_path.exists():
                print(f"  [skip] {category}/{preset_name}.py")
                continue

            content = make_preset(
                category=category,
                name=preset_name,
                theme=data["theme"],
                subject=data["subject"],
                scene=data["scene"],
                style=data["style"],
                lighting=data["lighting"],
                composition=data["composition"],
                quality=data["quality"],
            )
            file_path.write_text(content, encoding="utf-8")
            print(f"  [new]  {category}/{preset_name}.py")
            created += 1

    print()
    print(f"共创建 {created} 个新预设")


if __name__ == "__main__":
    main()