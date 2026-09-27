# scripts/expand_presets_4.py
"""
第四批：纹样、书法、家具、兵器、神兽、文人雅集、节日、交通工具
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
    # 纹样
    # ============================================================
    "pattern": {
        "cloud_pattern": {
            "theme": "云纹",
            "subject": [
                "auspicious clouds pattern, stylized ruyi shape, "
                "flowing lines, decorative motif",
                "a band of cloud patterns, "
                "layered scrolls, ceremonial decoration",
                "dense cloud pattern, "
                "interlocking ruyi, "
                "imperial textile",
            ],
            "scene": [
                "imperial robe, cloud pattern border",
                "porcelain vase, cloud motif decoration",
                "mural background, cloud scrolls",
            ],
            "style": [
                "traditional Chinese decorative pattern, "
                "gongbi precise lines, mineral pigments",
                "textile design, brocade pattern",
                "porcelain decoration, blue-and-white",
            ],
            "lighting": [
                "flat decorative lighting",
                "soft textile light",
                "museum light",
            ],
            "composition": [
                "square format",
                "horizontal band",
                "vertical panel",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "traditional Chinese cloud pattern",
                "8k uhd, refined decorative art",
            ],
        },
        "dragon_pattern": {
            "theme": "龙纹",
            "subject": [
                "imperial dragon pattern, five-clawed, "
                "frontal pose, surrounded by clouds",
                "a pair of dragons, "
                "facing a flaming pearl, "
                "imperial motif",
                "a dragon coiled around a column, "
                "scales and claws, "
                "imperial architecture",
            ],
            "scene": [
                "imperial robe, dragon roundel",
                "palace ceiling, dragon decoration",
                "porcelain plate, dragon motif",
            ],
            "style": [
                "imperial Chinese dragon pattern, "
                "mineral pigments, gold accents",
                "textile design, silk brocade",
                "porcelain decoration",
            ],
            "lighting": [
                "flat decorative lighting",
                "gold accent glow",
                "imperial radiance",
            ],
            "composition": [
                "square roundel",
                "vertical panel",
                "horizontal band",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "imperial Chinese dragon pattern",
                "8k uhd, refined imperial art",
            ],
        },
        "hui_pattern": {
            "theme": "回纹",
            "subject": [
                "interlocking key-fret pattern, "
                "angular spirals, "
                "ceremonial border",
                "a band of hui pattern, "
                "geometric, "
                "bronze vessel rim",
                "hui motif grid, "
                "continuous meander, "
                "architectural decoration",
            ],
            "scene": [
                "bronze vessel, hui pattern border",
                "architecture, beam decoration",
                "porcelain rim, hui motif",
            ],
            "style": [
                "traditional Chinese geometric pattern, "
                "precise ruled lines, "
                "bronze-age aesthetic",
                "decorative pattern, "
                "seamless repeat",
                "architectural ornament",
            ],
            "lighting": [
                "flat lighting",
                "soft museum light",
                "metallic sheen",
            ],
            "composition": [
                "horizontal band",
                "square grid",
                "vertical panel",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "traditional Chinese hui pattern",
                "8k uhd, geometric precision",
            ],
        },
        "baoxiang_flower": {
            "theme": "宝相花",
            "subject": [
                "baoxiang flower pattern, "
                "layered petals, "
                "auspicious Buddhist motif",
                "a grand baoxiang flower, "
                "centered, "
                "imperial roundel",
                "baoxiang flowers, "
                "interlocking, "
                "textile pattern",
            ],
            "scene": [
                "Buddhist mural, baoxiang decoration",
                "imperial robe, baoxiang motif",
                "cave ceiling, baoxiang roundel",
            ],
            "style": [
                "Tang dynasty baoxiang flower, "
                "mineral pigments, gongbi",
                "Buddhist decorative pattern",
                "textile design, silk brocade",
            ],
            "lighting": [
                "soft museum light",
                "celestial radiance",
                "cave lamplight",
            ],
            "composition": [
                "square roundel",
                "horizontal band",
                "vertical panel",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Tang dynasty baoxiang flower pattern",
                "8k uhd, Buddhist elegance",
            ],
        },
        "interlocking_floral": {
            "theme": "缠枝纹",
            "subject": [
                "interlocking floral scrolls, "
                "continuous vine, "
                "lotus flowers",
                "a band of interlocking florals, "
                "vine and blossoms, "
                "porcelain decoration",
                "a rich floral scroll, "
                "peonies and vines, "
                "imperial motif",
            ],
            "scene": [
                "porcelain vase, interlocking floral scroll",
                "textile, interlocking pattern",
                "architecture, panel decoration",
            ],
            "style": [
                "traditional Chinese floral scroll, "
                "gongbi precise lines",
                "porcelain decoration, "
                "blue-and-white",
                "textile design, silk",
            ],
            "lighting": [
                "soft daylight",
                "museum light",
                "warm interior light",
            ],
            "composition": [
                "horizontal band",
                "vertical panel",
                "square grid",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "traditional Chinese interlocking floral pattern",
                "8k uhd, refined detail",
            ],
        },
        "taotie": {
            "theme": "饕餮纹",
            "subject": [
                "taotie mask pattern, "
                "glaring eyes, horns, fangs, "
                "bronze-age motif",
                "a taotie face, "
                "symmetrical, "
                "on a bronze vessel",
                "a taotie pattern band, "
                "ritual vessel, "
                "Shang dynasty",
            ],
            "scene": [
                "bronze ritual vessel, taotie pattern",
                "archaeological illustration, taotie",
                "temple, taotie decoration",
            ],
            "style": [
                "Shang dynasty bronze motif, "
                "mineral pigments, precise details",
                "archaeological illustration",
                "bronze texture, patina",
            ],
            "lighting": [
                "museum light",
                "dramatic",
                "candlelight",
            ],
            "composition": [
                "square panel",
                "horizontal band",
                "vertical column",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "ancient Chinese taotie pattern",
                "8k uhd, bronze-age aesthetic",
            ],
        },
    },

    # ============================================================
    # 书法
    # ============================================================
    "calligraphy": {
        "kaishu": {
            "theme": "楷书",
            "subject": [
                "formal kaishu calligraphy, "
                "clear strokes, "
                "in the style of Yan Zhenqing",
                "a poem in kaishu, "
                "regular script, "
                "in the style of Ouyang Xun",
                "kaishu calligraphy, "
                "imperial edict, "
                "formal",
            ],
            "scene": [
                "xuan paper, ink stone, brush",
                "imperial court, edict document",
                "scholar's studio, "
                "scroll with calligraphy",
            ],
            "style": [
                "formal kaishu calligraphy, "
                "black ink on xuan paper",
                "traditional Chinese calligraphy, "
                "brush strokes",
                "letterpress print style",
            ],
            "lighting": [
                "soft daylight",
                "warm candlelight",
                "studio light",
            ],
            "composition": [
                "vertical scroll",
                "horizontal scroll",
                "square panel",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "traditional Chinese kaishu calligraphy",
                "8k uhd, refined brushwork",
            ],
        },
        "xingshu": {
            "theme": "行书",
            "subject": [
                "running script calligraphy, "
                "flowing strokes, "
                "in the style of Wang Xizhi",
                "a poem in xingshu, "
                "semi-cursive, "
                "elegant",
                "xingshu calligraphy, "
                "letter, "
                "in the style of Wang Xizhi's Lanting",
            ],
            "scene": [
                "xuan paper, ink stone",
                "scholar's studio, letter",
                "willow pavilion, spring",
            ],
            "style": [
                "xingshu calligraphy, "
                "flowing brushwork",
                "traditional Chinese calligraphy",
                "Wang Xizhi style",
            ],
            "lighting": [
                "soft daylight",
                "candlelight, intimate",
                "spring light",
            ],
            "composition": [
                "horizontal scroll",
                "vertical scroll",
                "square panel",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "traditional Chinese xingshu calligraphy",
                "8k uhd, elegant brushwork",
            ],
        },
        "caoshu": {
            "theme": "草书",
            "subject": [
                "wild cursive calligraphy, "
                "unrestrained strokes, "
                "in the style of Zhang Xu",
                "a poem in caoshu, "
                "continuous lines, "
                "expressive",
                "caoshu calligraphy, "
                "in the style of Huai Su",
            ],
            "scene": [
                "xuan paper, "
                "ink, "
                "scholar's studio",
                "wine cups, "
                "spring, "
                "inspiration",
                "moonlit garden, "
                "calligraphy",
            ],
            "style": [
                "wild cursive calligraphy, "
                "expressive brushwork",
                "Zhang Xu and Huai Su style",
                "traditional Chinese calligraphy",
            ],
            "lighting": [
                "dramatic light",
                "candlelight",
                "moonlight",
            ],
            "composition": [
                "horizontal scroll",
                "vertical scroll",
                "square panel",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "traditional Chinese wild cursive calligraphy",
                "8k uhd, expressive brushwork",
            ],
        },
        "lishu": {
            "theme": "隶书",
            "subject": [
                "clerk script calligraphy, "
                "flattened form, "
                "Han dynasty style",
                "a stele inscription in lishu, "
                "formal, "
                "Han dynasty",
                "lishu calligraphy, "
                "wide strokes, "
                "in the style of Cao Quan",
            ],
            "scene": [
                "stone stele, lishu inscription",
                "xuan paper, "
                "brush, "
                "ink stone",
                "imperial edict, "
                "Han dynasty",
            ],
            "style": [
                "Han dynasty lishu calligraphy, "
                "flat and wide strokes",
                "stele style",
                "traditional Chinese calligraphy",
            ],
            "lighting": [
                "museum light",
                "soft daylight",
                "stone texture",
            ],
            "composition": [
                "vertical stele",
                "horizontal scroll",
                "square panel",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Han dynasty lishu calligraphy",
                "8k uhd, stele texture",
            ],
        },
        "zhuanshu": {
            "theme": "篆书",
            "subject": [
                "seal script calligraphy, "
                "curved strokes, "
                "in the style of Li Si",
                "a small seal script, "
                "bronze vessel inscription, "
                "Shang dynasty",
                "zhuanshu calligraphy, "
                "square and rounded, "
                "imperial seal",
            ],
            "scene": [
                "bronze vessel, zhuanshu inscription",
                "imperial seal, "
                "jade, "
                "zhuanshu",
                "xuan paper, "
                "brush, "
                "zhuanshu practice",
            ],
            "style": [
                "small seal script calligraphy, "
                "curved and rounded",
                "bronze-age style",
                "traditional Chinese calligraphy",
            ],
            "lighting": [
                "museum light",
                "bronze patina",
                "soft daylight",
            ],
            "composition": [
                "vertical column",
                "square seal",
                "horizontal band",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "traditional Chinese zhuanshu calligraphy",
                "8k uhd, refined curves",
            ],
        },
        "kuangcao": {
            "theme": "狂草",
            "subject": [
                "mad cursive calligraphy, "
                "wild and free, "
                "in the style of Zhang Xu",
                "an explosive caoshu, "
                "unrestrained strokes, "
                "drunken poem",
                "kuangcao calligraphy, "
                "in the style of Huai Su",
            ],
            "scene": [
                "xuan paper, "
                "ink splatters, "
                "wild brushwork",
                "moonlit studio, "
                "wine cups",
                "scholar's garden, "
                "wild calligraphy",
            ],
            "style": [
                "mad cursive calligraphy, "
                "explosive brushwork",
                "Zhang Xu and Huai Su style",
                "drunken calligraphy",
            ],
            "lighting": [
                "dramatic light",
                "moonlight",
                "candlelight",
            ],
            "composition": [
                "horizontal scroll",
                "vertical scroll",
                "square panel",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "traditional Chinese kuangcao calligraphy",
                "8k uhd, explosive expression",
            ],
        },
    },

    # ============================================================
    # 家具
    # ============================================================
    "furniture": {
        "table": {
            "theme": "案",
            "subject": [
                "a Chinese altar table, "
                "dark wood, "
                "with porcelain vase",
                "a scholar's desk, "
                "with brush, ink stone, xuan paper",
                "a long narrow table, "
                "with incense burner",
            ],
            "scene": [
                "scholar's studio, "
                "table, "
                "bamboo",
                "imperial hall, "
                "long table, "
                "ceremonial",
                "garden pavilion, "
                "stone table, "
                "tea set",
            ],
            "style": [
                "Chinese gongbi still life, "
                "precise furniture details",
                "literati painting, "
                "xieyi freehand",
                "scholar's studio aesthetic",
            ],
            "lighting": [
                "soft interior light",
                "candlelight",
                "afternoon sunlight",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese furniture painting",
                "8k uhd, refined craftsmanship",
            ],
        },
        "couch": {
            "theme": "榻",
            "subject": [
                "a Chinese couch, "
                "wood frame, "
                "silk cushions",
                "a scholar reclining on a couch, "
                "reading, "
                "relaxed",
                "a couch with tea set, "
                "in a garden pavilion",
            ],
            "scene": [
                "scholar's studio, "
                "couch, books",
                "garden pavilion, "
                "couch, moonlight",
                "imperial bedroom, "
                "couch",
            ],
            "style": [
                "Chinese gongbi figure painting",
                "literati painting, "
                "xieyi freehand",
                "scholar's studio aesthetic",
            ],
            "lighting": [
                "soft interior light",
                "moonlight",
                "afternoon sunlight",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed",
                "8k uhd, elegant repose",
            ],
        },
        "chair": {
            "theme": "椅",
            "subject": [
                "a Chinese armchair, "
                "horseshoe back, "
                "dark wood",
                "a pair of side chairs, "
                "with silk cushions",
                "a scholar sitting in a chair, "
                "with a book",
            ],
            "scene": [
                "scholar's studio, "
                "chair, desk",
                "imperial hall, "
                "chairs, "
                "ceremonial",
                "garden pavilion, "
                "chairs, tea",
            ],
            "style": [
                "Chinese gongbi still life, "
                "precise furniture",
                "literati painting, "
                "xieyi freehand",
                "imperial palace aesthetic",
            ],
            "lighting": [
                "soft interior light",
                "candlelight",
                "afternoon sunlight",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square album leaf",
                "horizontal handscroll",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese furniture painting",
                "8k uhd, refined craftsmanship",
            ],
        },
        "small_table": {
            "theme": "几",
            "subject": [
                "a small tea table, "
                "with a teapot and cups",
                "a low incense table, "
                "with bronze incense burner",
                "a flower stand, "
                "with a vase of plum blossoms",
            ],
            "scene": [
                "scholar's studio, "
                "tea table, bamboo",
                "temple, incense table",
                "garden, flower stand, "
                "plum blossoms",
            ],
            "style": [
                "Chinese gongbi still life",
                "literati painting, "
                "minimal",
                "zen aesthetic",
            ],
            "lighting": [
                "soft interior light",
                "candlelight",
                "morning light",
            ],
            "composition": [
                "square album leaf",
                "vertical hanging scroll, lidu",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed",
                "8k uhd, refined elegance",
            ],
        },
        "cabinet": {
            "theme": "柜",
            "subject": [
                "a Chinese medicine cabinet, "
                "many small drawers, "
                "brass pulls",
                "a book cabinet, "
                "with scrolls and books",
                "a display cabinet, "
                "with porcelain and jade",
            ],
            "scene": [
                "scholar's studio, "
                "cabinet, desk",
                "apothecary, "
                "medicine cabinet",
                "imperial hall, "
                "display cabinet",
            ],
            "style": [
                "Chinese gongbi still life",
                "literati painting, "
                "precise details",
                "archaeological illustration",
            ],
            "lighting": [
                "soft interior light",
                "afternoon sunlight",
                "museum light",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square album leaf",
                "horizontal handscroll",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese furniture painting",
                "8k uhd, refined woodwork",
            ],
        },
        "screen": {
            "theme": "屏",
            "subject": [
                "a folding screen, "
                "with landscape painting, "
                "gold leaf background",
                "a single-panel screen, "
                "with calligraphy",
                "a room divider, "
                "with painted scenes",
            ],
            "scene": [
                "scholar's studio, "
                "screen, table",
                "imperial hall, "
                "gold screen",
                "tea room, "
                "bamboo screen",
            ],
            "style": [
                "Japanese byobu screen painting, "
                "gold leaf background",
                "Chinese gongbi screen painting",
                "Rinpa school style",
            ],
            "lighting": [
                "soft interior light",
                "gold leaf glow",
                "afternoon sunlight",
            ],
            "composition": [
                "horizontal multi-panel",
                "vertical panel",
                "square panel",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "traditional folding screen painting",
                "8k uhd, gold leaf elegance",
            ],
        },
    },

    # ============================================================
    # 兵器
    # ============================================================
    "weapon": {
        "sword": {
            "theme": "剑",
            "subject": [
                "a Chinese jian sword, "
                "straight blade, "
                "with scabbard and tassel",
                "a scholar with a sword, "
                "contemplative, "
                "in a garden",
                "a pair of swords, "
                "on a stand, "
                "scholar's studio",
            ],
            "scene": [
                "scholar's studio, "
                "sword on stand",
                "bamboo grove, "
                "sword, "
                "moonlight",
                "mountain peak, "
                "sword, "
                "mist",
            ],
            "style": [
                "Chinese gongbi weapon painting, "
                "precise details, metallic sheen",
                "literati painting, "
                "xieyi freehand",
                "martial arts aesthetic",
            ],
            "lighting": [
                "dramatic light, "
                "metallic gleam",
                "moonlight, "
                "silver blade",
                "candlelight",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square album leaf",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "traditional Chinese sword painting",
                "8k uhd, martial spirit",
            ],
        },
        "saber": {
            "theme": "刀",
            "subject": [
                "a Chinese dao saber, "
                "curved blade, "
                "with tassel and scabbard",
                "a general with a saber, "
                "imposing posture",
                "a pair of sabers, "
                "crossed, "
                "on a rack",
            ],
            "scene": [
                "military camp, "
                "sabers, banner",
                "mountain pass, "
                "warrior, "
                "saber",
                "imperial palace, "
                "ceremonial saber",
            ],
            "style": [
                "Chinese gongbi weapon painting, "
                "precise metallic details",
                "mural painting, "
                "martial style",
                "literati painting, "
                "xieyi freehand",
            ],
            "lighting": [
                "dramatic light, "
                "metallic gleam",
                "sunset, "
                "silhouette",
                "moonlight",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "horizontal handscroll",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed",
                "8k uhd, martial valor",
            ],
        },
        "bow": {
            "theme": "弓",
            "subject": [
                "a Chinese recurve bow, "
                "with arrows and quiver",
                "an archer drawing a bow, "
                "focused, "
                "mountain range",
                "a bow on a stand, "
                "with arrows",
            ],
            "scene": [
                "mountain pass, "
                "archer, "
                "banner",
                "hunting ground, "
                "bow, "
                "deer",
                "military camp, "
                "bows, arrows",
            ],
            "style": [
                "Chinese gongbi weapon painting",
                "mural painting, "
                "martial style",
                "literati painting, "
                "xieyi freehand",
            ],
            "lighting": [
                "dramatic light, "
                "sunset",
                "dawn light",
                "moonlight",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "horizontal handscroll",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed",
                "8k uhd, martial precision",
            ],
        },
        "spear": {
            "theme": "枪",
            "subject": [
                "a Chinese spear, "
                "long shaft, "
                "red tassel",
                "a warrior with a spear, "
                "dynamic pose",
                "a set of spears, "
                "on a rack",
            ],
            "scene": [
                "military camp, "
                "spears, banners",
                "battlefield, "
                "smoke, "
                "spear",
                "mountain pass, "
                "warrior",
            ],
            "style": [
                "Chinese gongbi weapon painting",
                "mural painting, "
                "martial style",
                "literati painting, "
                "xieyi freehand",
            ],
            "lighting": [
                "dramatic light",
                "sunset",
                "stormy sky",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "horizontal handscroll",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed",
                "8k uhd, martial power",
            ],
        },
        "halberd": {
            "theme": "戟",
            "subject": [
                "a Chinese halberd, "
                "with side blade, "
                "ceremonial",
                "a general with a halberd, "
                "imposing, "
                "at a gate",
                "a pair of halberds, "
                "crossed, "
                "on a stand",
            ],
            "scene": [
                "imperial palace gate, "
                "halberds, guards",
                "military camp, "
                "halberds, banners",
                "battlefield, "
                "general, "
                "halberd",
            ],
            "style": [
                "Chinese gongbi weapon painting",
                "mural painting, "
                "martial style",
                "imperial ceremony",
            ],
            "lighting": [
                "dramatic light",
                "sunset, silhouette",
                "torchlight",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "horizontal handscroll",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed",
                "8k uhd, martial grandeur",
            ],
        },
        "armor": {
            "theme": "甲胄",
            "subject": [
                "a Chinese general in full armor, "
                "lacquered plates, "
                "imposing posture",
                "a set of armor on a stand, "
                "helmet, "
                "scholar's studio",
                "a warrior with a sword, "
                "in armor, "
                "mountain range",
            ],
            "scene": [
                "military camp, "
                "armor, banner",
                "imperial palace, "
                "armor, "
                "ceremonial",
                "battlefield, "
                "armor, "
                "smoke",
            ],
            "style": [
                "Chinese gongbi armor painting, "
                "precise details, "
                "mineral pigments",
                "mural painting, "
                "martial style",
                "in the style of Qing dynasty",
            ],
            "lighting": [
                "dramatic light, "
                "metallic gleam",
                "sunset",
                "torchlight",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "horizontal handscroll",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "traditional Chinese armor painting",
                "8k uhd, martial spirit",
            ],
        },
    },

    # ============================================================
    # 神兽
    # ============================================================
    "mythical": {
        "dragon": {
            "theme": "龙",
            "subject": [
                "a Chinese dragon, "
                "long serpentine body, "
                "in clouds",
                "a five-clawed imperial dragon, "
                "frontal, "
                "with flaming pearl",
                "a dragon emerging from waves, "
                "scales and claws, "
                "imperial symbol",
            ],
            "scene": [
                "stormy sky, "
                "clouds, lightning",
                "ocean waves, "
                "dragon rising",
                "mountain peak, "
                "dragon coiled",
            ],
            "style": [
                "traditional Chinese dragon painting, "
                "in the style of Chen Rong",
                "gongbi dragon painting, "
                "precise scales, mineral pigments",
                "ink and wash dragon, xieyi",
            ],
            "lighting": [
                "storm light, dramatic",
                "celestial radiance",
                "sunset, golden",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "horizontal handscroll",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "traditional Chinese dragon painting",
                "8k uhd, imperial grandeur",
            ],
        },
        "phoenix": {
            "theme": "凤",
            "subject": [
                "a Chinese phoenix, "
                "magnificent plumage, "
                "long tail feathers",
                "two phoenixes, "
                "yin-yang, "
                "courtship dance",
                "a phoenix on a wutong tree, "
                "auspicious, "
                "spring",
            ],
            "scene": [
                "imperial palace, "
                "peonies, "
                "golden tiles",
                "auspicious clouds, "
                "sun disc",
                "wutong tree, "
                "spring garden",
            ],
            "style": [
                "traditional Chinese phoenix painting, "
                "mineral pigments, gold leaf",
                "gongbi phoenix painting, "
                "intricate feather details",
                "imperial court painting",
            ],
            "lighting": [
                "imperial radiance, "
                "golden glow",
                "celestial radiance",
                "sunrise",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square album leaf",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "auspicious Chinese phoenix painting",
                "8k uhd, celestial elegance",
            ],
        },
        "qilin": {
            "theme": "麒麟",
            "subject": [
                "a qilin, "
                "deer-like body, dragon scales, "
                "auspicious beast",
                "a qilin with a boy, "
                "auspicious scene, "
                "folk painting",
                "a qilin in a garden, "
                "peaceful, auspicious",
            ],
            "scene": [
                "imperial garden, "
                "peonies",
                "auspicious clouds, "
                "sun",
                "mountain path, "
                "bamboo",
            ],
            "style": [
                "traditional Chinese painting, "
                "mineral pigments, gongbi",
                "Ming dynasty court painting",
                "folk painting style",
            ],
            "lighting": [
                "auspicious radiance",
                "warm sunlight",
                "celestial glow",
            ],
            "composition": [
                "square album leaf",
                "vertical hanging scroll, lidu",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed",
                "8k uhd, auspicious blessing",
            ],
        },
        "white_tiger": {
            "theme": "白虎",
            "subject": [
                "a white tiger, "
                "one of the four celestial animals, "
                "west direction",
                "a roaring white tiger, "
                "mountain peak, "
                "dramatic",
                "a white tiger in snow, "
                "silent, "
                "majestic",
            ],
            "scene": [
                "mountain peak, "
                "storm, "
                "dramatic sky",
                "snow-covered mountain, "
                "silent",
                "bamboo grove at night, "
                "moonlight",
            ],
            "style": [
                "traditional Chinese tiger painting, "
                "ink and wash, xieyi",
                "gongbi tiger painting, "
                "precise fur",
                "dramatic brushwork",
            ],
            "lighting": [
                "moonlit, dramatic",
                "snow light, cool",
                "stormy sky",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "horizontal handscroll",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "celestial white tiger painting",
                "8k uhd, divine power",
            ],
        },
        "black_tortoise": {
            "theme": "玄武",
            "subject": [
                "the black tortoise, "
                "snake coiled around, "
                "north direction",
                "a giant tortoise, "
                "with serpent, "
                "celestial beast",
                "a black tortoise, "
                "mountain stream, "
                "mystical",
            ],
            "scene": [
                "deep water, "
                "mountain stream, "
                "mystical",
                "northern sky, "
                "stars, "
                "celestial",
                "stone bridge, "
                "river, "
                "tortoise",
            ],
            "style": [
                "traditional Chinese mythical painting, "
                "ink and wash, xieyi",
                "gongbi tortoise painting, "
                "precise scales",
                "celestial symbol painting",
            ],
            "lighting": [
                "moonlight, mystical",
                "deep water light",
                "celestial glow",
            ],
            "composition": [
                "square album leaf",
                "vertical hanging scroll, lidu",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "celestial black tortoise painting",
                "8k uhd, mysterious power",
            ],
        },
        "vermilion_bird": {
            "theme": "朱雀",
            "subject": [
                "the vermilion bird, "
                "south direction, "
                "fire-red plumage",
                "a red bird flying, "
                "flames, "
                "celestial",
                "a vermilion bird perched, "
                "sun, "
                "imperial symbol",
            ],
            "scene": [
                "burning sky, "
                "sun disc, "
                "celestial",
                "southern mountains, "
                "flames, "
                "dramatic",
                "imperial palace, "
                "sun, "
                "auspicious",
            ],
            "style": [
                "traditional Chinese celestial painting, "
                "mineral pigments, gold accents",
                "gongbi bird painting, "
                "flame details",
                "imperial symbol painting",
            ],
            "lighting": [
                "fire light, dramatic",
                "sunrise, golden",
                "celestial radiance",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square album leaf",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "celestial vermilion bird painting",
                "8k uhd, fire elegance",
            ],
        },
    },

    # ============================================================
    # 文人雅集
    # ============================================================
    "literati_gathering": {
        "lanting": {
            "theme": "兰亭雅集",
            "subject": [
                "a group of scholars at a stream, "
                "wine cups floating on water, "
                "writing poetry, "
                "in the style of Wang Xizhi's Lanting",
                "Wang Xizhi writing the Lanting Xu, "
                "surrounded by scholars, "
                "spring",
                "orchid pavilion, "
                "scholars gathered, "
                "calligraphy",
            ],
            "scene": [
                "mountain stream, "
                "orchids, "
                "bamboo grove",
                "pavilion, "
                "spring, "
                "tea and wine",
                "misty mountain, "
                "stream, "
                "birdsong",
            ],
            "style": [
                "traditional Chinese gathering painting, "
                "gongbi figures, precise details",
                "in the style of Wen Zhengming, "
                "elegant refinement",
                "literati painting, xieyi freehand",
            ],
            "lighting": [
                "spring morning light, warm",
                "soft afternoon light",
                "sunset, warm glow",
            ],
            "composition": [
                "horizontal handscroll",
                "square album leaf",
                "vertical hanging scroll, lidu",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Lanting gathering painting",
                "8k uhd, elegant literati",
            ],
        },
        "bamboo_seven": {
            "theme": "竹林七贤",
            "subject": [
                "seven sages in a bamboo grove, "
                "drinking wine, playing music, "
                "in the style of Ruan Ji and Xi Kang",
                "a scholar playing the guqin, "
                "bamboo grove, "
                "others listening",
                "seven sages, "
                "contemplative, "
                "drunken revelry",
            ],
            "scene": [
                "bamboo grove, "
                "stream, "
                "rocks",
                "mountain valley, "
                "mist, "
                "birds",
                "moonlit bamboo, "
                "banquet, "
                "wine",
            ],
            "style": [
                "traditional Chinese figure painting, "
                "gongbi figures, precise details",
                "in the style of Sun Wei and Li Gonglin",
                "literati painting, xieyi freehand",
            ],
            "lighting": [
                "dappled bamboo light",
                "moonlight, silver",
                "sunset, warm",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Seven Sages of the Bamboo Grove",
                "8k uhd, philosophical atmosphere",
            ],
        },
        "xishan": {
            "theme": "西园雅集",
            "subject": [
                "a grand garden gathering, "
                "painters, poets, calligraphers, "
                "in the style of Li Gonglin",
                "Su Shi and Mi Fu "
                "in a garden, "
                "painting and calligraphy",
                "imperial garden, "
                "scholars, "
                "peonies",
            ],
            "scene": [
                "imperial garden, "
                "peonies, "
                "rockery",
                "stream, "
                "pavilion, "
                "willow trees",
                "misty morning, "
                "garden, "
                "birds",
            ],
            "style": [
                "traditional Chinese gathering painting, "
                "gongbi figures, precise details",
                "in the style of Li Gonglin",
                "literati painting, xieyi freehand",
            ],
            "lighting": [
                "spring morning light",
                "afternoon, dappled",
                "sunset, warm",
            ],
            "composition": [
                "horizontal handscroll",
                "square album leaf",
                "vertical hanging scroll, lidu",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Xiyuan gathering painting",
                "8k uhd, refined literati",
            ],
        },
        "spring_pavilion": {
            "theme": "香山雅集",
            "subject": [
                "a group of elderly scholars, "
                "gathered in a pavilion, "
                "writing poetry, "
                "in the style of Bai Juyi",
                "Bai Juyi with friends, "
                "wine, poetry, "
                "mountain pavilion",
                "nine elders, "
                "poetry gathering, "
                "autumn",
            ],
            "scene": [
                "mountain pavilion, "
                "autumn, "
                "red maple",
                "stream, "
                "rocks, "
                "birds",
                "misty mountain, "
                "pine, "
                "poetry",
            ],
            "style": [
                "traditional Chinese gathering painting",
                "gongbi figures, precise details",
                "literati painting, xieyi freehand",
            ],
            "lighting": [
                "autumn light, warm",
                "sunset, orange-red",
                "morning mist",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed",
                "8k uhd, autumnal elegance",
            ],
        },
        "zui_weng": {
            "theme": "醉翁亭",
            "subject": [
                "Ouyang Xiu drinking wine, "
                "in a mountain pavilion, "
                "joyful atmosphere",
                "scholars gathered at a pavilion, "
                "wine, food, "
                "mountain range",
                "a stone pavilion, "
                "spring, "
                "scholars",
            ],
            "scene": [
                "mountain pavilion, "
                "spring, "
                "forest",
                "stream, "
                "rocks, "
                "birds",
                "misty mountain, "
                "pine, "
                "wine cups",
            ],
            "style": [
                "traditional Chinese gathering painting",
                "gongbi figures, precise details",
                "in the style of Wen Zhengming",
            ],
            "lighting": [
                "spring morning light",
                "afternoon, warm",
                "sunset",
            ],
            "composition": [
                "horizontal handscroll",
                "square album leaf",
                "vertical hanging scroll, lidu",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed",
                "8k uhd, joyful literati",
            ],
        },
        "qushui": {
            "theme": "曲水流觞",
            "subject": [
                "scholars seated along a winding stream, "
                "wine cups floating, "
                "writing poems, "
                "in the style of Lanting",
                "cups floating on water, "
                "scholars drinking, "
                "poetry",
                "a winding stream, "
                "scholars, "
                "spring",
            ],
            "scene": [
                "winding stream, "
                "rocks, "
                "bamboo",
                "spring garden, "
                "peonies, "
                "willow trees",
                "misty mountain, "
                "stream, "
                "birdsong",
            ],
            "style": [
                "traditional Chinese gathering painting",
                "gongbi figures, precise details",
                "literati painting, xieyi freehand",
            ],
            "lighting": [
                "spring morning light",
                "afternoon, warm",
                "sunset",
            ],
            "composition": [
                "horizontal handscroll",
                "square album leaf",
                "vertical hanging scroll, lidu",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "qushui liushang gathering painting",
                "8k uhd, refined literati",
            ],
        },
    },

    # ============================================================
    # 节日
    # ============================================================
    "festival": {
        "spring_festival": {
            "theme": "春节",
            "subject": [
                "a Chinese New Year scene, "
                "red lanterns, "
                "firecrackers, "
                "family reunion dinner",
                "children playing with firecrackers, "
                "red couplets, "
                "new year",
                "a lion dance, "
                "crowd, "
                "firecrackers",
            ],
            "scene": [
                "village, red lanterns, "
                "snow, warm windows",
                "imperial palace, "
                "banquet, firecrackers",
                "town street, "
                "red decorations, "
                "festive",
            ],
            "style": [
                "Chinese folk painting, "
                "vibrant red, "
                "gongbi details",
                "traditional Chinese festival painting",
                "New Year print style",
            ],
            "lighting": [
                "lantern light, warm",
                "firecracker light",
                "snow reflection",
            ],
            "composition": [
                "horizontal handscroll",
                "square album leaf",
                "vertical hanging scroll, lidu",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese New Year painting",
                "8k uhd, festive joy",
            ],
        },
        "lantern_festival": {
            "theme": "元宵节",
            "subject": [
                "a Chinese lantern festival, "
                "colorful lanterns, "
                "crowds, "
                "riddles",
                "lantern riddles, "
                "scholars guessing, "
                "night",
                "a lantern parade, "
                "river, "
                "moon",
            ],
            "scene": [
                "city street, "
                "lanterns, "
                "night",
                "river, "
                "floating lanterns, "
                "moon",
                "imperial palace, "
                "lantern show, "
                "crowd",
            ],
            "style": [
                "Chinese folk painting, "
                "vibrant colors, "
                "gongbi details",
                "traditional Chinese festival painting",
                "night scene painting",
            ],
            "lighting": [
                "lantern light, colorful",
                "moonlight",
                "fireworks",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese lantern festival painting",
                "8k uhd, festive night",
            ],
        },
        "dragon_boat": {
            "theme": "端午",
            "subject": [
                "a dragon boat race, "
                "rowers, drums, "
                "crowd cheering",
                "zongzi, "
                "bamboo leaves, "
                "river",
                "Qu Yuan, "
                "riverside, "
                "melancholy",
            ],
            "scene": [
                "river, "
                "dragon boats, "
                "crowd",
                "village, "
                "zongzi, "
                "summer",
                "mountain river, "
                "boat, "
                "reeds",
            ],
            "style": [
                "Chinese folk painting, "
                "vibrant colors, gongbi details",
                "traditional Chinese festival painting",
                "Qingming Scroll style",
            ],
            "lighting": [
                "summer sunlight, bright",
                "morning light",
                "afternoon",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "dragon boat festival painting",
                "8k uhd, dynamic race",
            ],
        },
        "mid_autumn": {
            "theme": "中秋",
            "subject": [
                "a moon viewing gathering, "
                "scholars, mooncakes, "
                "full moon",
                "a family reunion, "
                "mooncakes, "
                "lanterns, "
                "moon",
                "osmanthus flowers, "
                "moon, "
                "jade rabbit",
            ],
            "scene": [
                "garden, "
                "full moon, "
                "osmanthus",
                "pavilion, "
                "moonlight, "
                "tea",
                "river, "
                "moon, "
                "lanterns",
            ],
            "style": [
                "Chinese festival painting, "
                "gongbi details",
                "literati painting, moon viewing",
                "traditional autumn painting",
            ],
            "lighting": [
                "moonlight, silver",
                "lantern light, warm",
                "twilight, purple",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Mid-Autumn festival painting",
                "8k uhd, moonlit reunion",
            ],
        },
        "double_ninth": {
            "theme": "重阳",
            "subject": [
                "chrysanthemums, "
                "chongyang cake, "
                "wine cups, "
                "mountain climbing",
                "elderly scholars climbing a mountain, "
                "chrysanthemums, "
                "autumn",
                "a poem gathering, "
                "chrysanthemums, "
                "wine",
            ],
            "scene": [
                "mountain path, "
                "autumn, "
                "chrysanthemums",
                "pavilion, "
                "mountain peak, "
                "autumn",
                "garden, "
                "chrysanthemums, "
                "wine",
            ],
            "style": [
                "Chinese festival painting, "
                "gongbi details",
                "literati painting, autumn",
                "traditional autumn painting",
            ],
            "lighting": [
                "autumn sunlight, warm",
                "afternoon",
                "sunset",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Double Ninth festival painting",
                "8k uhd, autumnal elegance",
            ],
        },
        "qixi": {
            "theme": "七夕",
            "subject": [
                "the Cowherd and Weaver Girl "
                "meeting on a magpie bridge, "
                "stars, "
                "romantic",
                "a woman praying for skills, "
                "moon, "
                "needle and thread",
                "two lovers, "
                "Milky Way, "
                "magpies",
            ],
            "scene": [
                "night sky, "
                "Milky Way, "
                "stars",
                "courtyard, "
                "moon, "
                "needle and thread",
                "magpie bridge, "
                "river of stars",
            ],
            "style": [
                "Chinese festival painting, "
                "gongbi details, romantic",
                "traditional Chinese myth painting",
                "literati painting, romantic",
            ],
            "lighting": [
                "starlight, silver",
                "moonlight",
                "twilight, purple",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square album leaf",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Qixi festival painting",
                "8k uhd, romantic stars",
            ],
        },
    },

    # ============================================================
    # 交通工具
    # ============================================================
    "vehicle": {
        "sedan_chair": {
            "theme": "轿",
            "subject": [
                "a Chinese sedan chair, "
                "carried by bearers, "
                "in a mountain path",
                "a bridal sedan chair, "
                "red decorations, "
                "wedding procession",
                "an imperial sedan, "
                "yellow silk, "
                "attendants",
            ],
            "scene": [
                "mountain path, "
                "mist, "
                "pines",
                "city street, "
                "wedding procession, "
                "lanterns",
                "imperial palace, "
                "ceremonial"
            ],
            "style": [
                "Chinese gongbi painting, "
                "precise details, "
                "mineral pigments",
                "Qingming Scroll style",
                "traditional Chinese figure painting",
            ],
            "lighting": [
                "daylight, warm",
                "sunset, warm",
                "lantern light",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese sedan chair painting",
                "8k uhd, traditional transport",
            ],
        },
        "boat": {
            "theme": "船",
            "subject": [
                "a Chinese fishing boat, "
                "sail, "
                "on a misty river",
                "a scholar's boat, "
                "with a bamboo awning, "
                "river travel",
                "a dragon boat, "
                "rows of oarsmen, "
                "festival",
            ],
            "scene": [
                "misty river, "
                "distant mountains, "
                "willow trees",
                "mountain stream, "
                "rocks, "
                "reeds",
                "sea, "
                "waves, "
                "distant islands",
            ],
            "style": [
                "Chinese ink wash painting, "
                "minimal details",
                "literati painting, xieyi freehand",
                "Song dynasty river painting",
            ],
            "lighting": [
                "misty morning",
                "moonlight, silver",
                "sunset, warm",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "traditional Chinese boat painting",
                "8k uhd, atmospheric",
            ],
        },
        "cart": {
            "theme": "车",
            "subject": [
                "an ox-drawn cart, "
                "goods, "
                "on a mountain road",
                "a horse-drawn carriage, "
                "travelers, "
                "city gate",
                "a farm cart, "
                "harvest, "
                "rice field",
            ],
            "scene": [
                "mountain road, "
                "travelers, "
                "distant village",
                "city gate, "
                "crowd, "
                "market",
                "rice field, "
                "harvest, "
                "village",
            ],
            "style": [
                "Chinese ink wash painting, "
                "minimal details",
                "Qingming Scroll style",
                "traditional Chinese figure painting",
            ],
            "lighting": [
                "sunrise, warm",
                "daylight",
                "sunset",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed",
                "8k uhd, everyday life",
            ],
        },
        "horse": {
            "theme": "马",
            "subject": [
                "a Tang dynasty horse, "
                "plump powerful build, "
                "in the style of Han Gan",
                "a scholar riding a horse, "
                "in a mountain path",
                "a warrior on a horse, "
                "galloping, "
                "dynamic",
            ],
            "scene": [
                "mountain path, "
                "mist, "
                "pines",
                "open field, "
                "willow tree, "
                "distant mountains",
                "battlefield, "
                "smoke, "
                "distant peaks",
            ],
            "style": [
                "traditional Chinese horse painting, "
                "in the style of Han Gan and Zhao Mengfu",
                "gongbi horse painting, "
                "precise details, mineral pigments",
                "ink and wash horse, xieyi",
            ],
            "lighting": [
                "sunrise, warm",
                "daylight",
                "dramatic light",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Tang dynasty horse painting",
                "8k uhd, elegant power",
            ],
        },
        "camel": {
            "theme": "骆驼",
            "subject": [
                "a Bactrian camel, "
                "with goods, "
                "on a desert route",
                "a camel caravan, "
                "merchants, "
                "silk road",
                "a camel with a rider, "
                "sand dunes, "
                "sunset",
            ],
            "scene": [
                "desert, "
                "sand dunes, "
                "sunset",
                "silk road, "
                "oasis, "
                "distant mountains",
                "mountain pass, "
                "caravan, "
                "snow"
            ],
            "style": [
                "Tang dynasty painting, "
                "mineral pigments, precise details",
                "gongbi camel painting, "
                "precise details",
                "literati painting, xieyi",
            ],
            "lighting": [
                "sunset, golden",
                "desert light, warm",
                "moonlight, silver",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Tang dynasty camel painting",
                "8k uhd, silk road journey",
            ],
        },
        "raft": {
            "theme": "筏",
            "subject": [
                "a bamboo raft, "
                "with a fisherman, "
                "on a misty river",
                "a log raft, "
                "on a mountain stream, "
                "dramatic",
                "a bamboo raft, "
                "river, "
                "distant mountains",
            ],
            "scene": [
                "misty river, "
                "distant mountains, "
                "reeds",
                "mountain stream, "
                "rocks, "
                "waterfall",
                "sea, "
                "waves, "
                "islands",
            ],
            "style": [
                "Chinese ink wash painting, "
                "minimal details",
                "literati painting, xieyi freehand",
                "Song dynasty river painting",
            ],
            "lighting": [
                "misty morning",
                "moonlight, silver",
                "sunset, warm",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed",
                "8k uhd, atmospheric",
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