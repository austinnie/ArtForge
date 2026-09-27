# scripts/expand_presets_3.py
"""
第三批：山石、水景、气象、四季、果实、蔬果、器物、乐舞
共 8 类 42 个预设
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
    # 山石
    # ============================================================
    "mountain": {
        "peaks": {
            "theme": "奇峰",
            "subject": [
                "towering limestone peaks, "
                "dramatic vertical cliffs, misty valleys",
                "a cluster of sharp peaks rising from clouds, "
                "sunrise golden glow",
                "jagged mountain ridges, "
                "deep ravines, pine clinging to rock",
            ],
            "scene": [
                "cloud sea below peaks, "
                "sunrise, atmospheric perspective",
                "mountain range in mist, "
                "distant temple bell",
                "storm sky, dramatic shafts of light",
            ],
            "style": [
                "Chinese ink wash landscape, "
                "in the style of Fan Kuan and Guo Xi",
                "literati painting, xieyi freehand, "
                "monochrome ink, texture strokes (cunfa)",
                "Song dynasty monumental landscape, "
                "atmospheric depth",
            ],
            "lighting": [
                "sunrise light, golden peaks",
                "misty soft light, atmospheric",
                "storm light, dramatic",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "horizontal handscroll",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "traditional Chinese landscape painting",
                "8k uhd, subtle ink gradations",
            ],
        },
        "rocks": {
            "theme": "怪石",
            "subject": [
                "scholar's rock, gnarled and pitted, "
                "a natural sculpture, contemplation",
                "a strange rock formation, "
                "moss-covered, weathered",
                "three rocks, one tall, one low, "
                "one horizontal, composition",
            ],
            "scene": [
                "garden with rockery, "
                "bamboo and pine backdrop",
                "riverside rock, "
                "willow tree, autumn",
                "mountain path, rocks, "
                "distant peaks",
            ],
            "style": [
                "Chinese ink wash rock painting, "
                "in the style of Mi Fu",
                "literati painting, xieyi, "
                "texture strokes",
                "gongbi rock painting, "
                "precise textures",
            ],
            "lighting": [
                "soft daylight, textured shadows",
                "moonlight, dramatic",
                "rainy atmosphere",
            ],
            "composition": [
                "square album leaf",
                "vertical hanging scroll, lidu",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "traditional Chinese rock painting",
                "8k uhd, natural sculpture",
            ],
        },
        "cliff": {
            "theme": "悬崖",
            "subject": [
                "a sheer cliff dropping into abyss, "
                "pine trees clinging to rock",
                "a cliffside temple, "
                "stone steps winding up",
                "a cliff in mist, "
                "waterfall, distant peak",
            ],
            "scene": [
                "deep gorge, river below, "
                "birds soaring",
                "misty cliff, "
                "distant mountains, "
                "atmospheric",
                "stormy sky, "
                "cliff silhouette",
            ],
            "style": [
                "Chinese ink wash landscape, "
                "in the style of Ma Yuan",
                "literati painting, xieyi freehand",
                "Song dynasty landscape, "
                "one-corner composition",
            ],
            "lighting": [
                "morning light on cliff face",
                "moonlight, dramatic silhouette",
                "storm light, dramatic",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "horizontal handscroll",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "traditional Chinese cliff painting",
                "8k uhd, dramatic atmosphere",
            ],
        },
        "cave": {
            "theme": "溶洞",
            "subject": [
                "a mysterious mountain cave, "
                "stalactites, glowing light",
                "a cave entrance, "
                "bamboo, moss, ancient trees",
                "inside a cavern, "
                "stone formations, "
                "hidden waterfall",
            ],
            "scene": [
                "mountain interior, "
                "crystal formations, "
                "mysterious atmosphere",
                "cave entrance, "
                "mist, distant light",
                "underground river, "
                "stone bridges",
            ],
            "style": [
                "Chinese ink wash cave painting, "
                "atmospheric",
                "literati painting, mysterious",
                "modern Chinese landscape",
            ],
            "lighting": [
                "mysterious cave light",
                "shafts of light from entrance",
                "glowing mineral formations",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "horizontal handscroll",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "mysterious Chinese cave painting",
                "8k uhd",
            ],
        },
        "cliff_path": {
            "theme": "栈道",
            "subject": [
                "a narrow mountain path "
                "clinging to a cliff face, "
                "travelers with staffs",
                "a wooden plank walkway "
                "built on a cliff, "
                "mist, abyss below",
                "an ancient mountain pass, "
                "stone steps, "
                "distant travelers",
            ],
            "scene": [
                "deep gorge, cliff path, "
                "waterfall in distance",
                "misty mountains, "
                "stone steps, ancient trees",
                "stormy sky, "
                "path winding up",
            ],
            "style": [
                "Chinese ink wash landscape, "
                "in the style of Fan Kuan",
                "literati painting, xieyi",
                "Song dynasty landscape, "
                "dramatic mountain path",
            ],
            "lighting": [
                "morning light breaking through mist",
                "twilight, dramatic",
                "misty, ethereal",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "horizontal handscroll",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed",
                "8k uhd, heroic journey",
            ],
        },
    },

    # ============================================================
    # 水景
    # ============================================================
    "water": {
        "river": {
            "theme": "江河",
            "subject": [
                "a wide river, "
                "boat with fisherman, "
                "distant mountains",
                "river winding through "
                "mountains, bridges, travelers",
                "a great river, "
                "willow trees, "
                "setting sun",
            ],
            "scene": [
                "river valley, "
                "mountain backdrop, "
                "mist",
                "river town, "
                "stone bridge, "
                "boats, lanterns",
                "autumn river, "
                "reeds, wild geese",
            ],
            "style": [
                "Chinese ink wash river painting, "
                "in the style of Dong Yuan",
                "literati painting, xieyi freehand",
                "Song dynasty river landscape, "
                "atmospheric",
            ],
            "lighting": [
                "sunset, golden river",
                "misty morning, "
                "silver water",
                "moonlight, river",
            ],
            "composition": [
                "horizontal handscroll",
                "square album leaf",
                "vertical hanging scroll, lidu",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "traditional Chinese river painting",
                "8k uhd",
            ],
        },
        "lake": {
            "theme": "湖泊",
            "subject": [
                "a still lake, "
                "moon reflected, "
                "distant pavilion",
                "lake surrounded by mountains, "
                "willow trees, mist",
                "a lotus lake, "
                "boats, egrets",
            ],
            "scene": [
                "mountain lake, "
                "reflection of peaks",
                "lake pavilion, "
                "moon, willows",
                "misty lake, "
                "islands, "
                "distant temple",
            ],
            "style": [
                "Chinese ink wash lake painting, "
                "in the style of Mi Fu",
                "literati painting, xieyi, "
                "vast negative space",
                "Song dynasty lake landscape",
            ],
            "lighting": [
                "moonlight on lake, "
                "silver reflection",
                "dawn mist, "
                "atmospheric",
                "sunset, "
                "orange reflection",
            ],
            "composition": [
                "horizontal handscroll",
                "square album leaf",
                "vertical hanging scroll, lidu",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed",
                "8k uhd, serene atmosphere",
            ],
        },
        "sea": {
            "theme": "海",
            "subject": [
                "a rocky shore, "
                "waves crashing, "
                "seagulls, "
                "distant mountains",
                "a lone sailboat, "
                "vast ocean, "
                "sunrise",
                "sea rocks with pines, "
                "waves, "
                "moon",
            ],
            "scene": [
                "rocky coastline, "
                "waves, "
                "distant islands",
                "ocean sunrise, "
                "sailboat, "
                "mist",
                "stormy sea, "
                "waves, "
                "lighthouse",
            ],
            "style": [
                "Chinese ink wash sea painting, "
                "in the style of Ma Yuan",
                "literati painting, xieyi freehand",
                "traditional seascape",
            ],
            "lighting": [
                "sunrise, "
                "golden sea",
                "moonlight, "
                "silver waves",
                "stormy, "
                "dramatic",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed",
                "8k uhd, oceanic drama",
            ],
        },
        "stream": {
            "theme": "溪流",
            "subject": [
                "a mountain stream, "
                "clear water over pebbles, "
                "mossy rocks",
                "a small waterfall, "
                "pine trees, "
                "stone bridge",
                "a stream winding through bamboo, "
                "stone lantern, "
                "scholar",
            ],
            "scene": [
                "mountain valley, "
                "pine trees, "
                "rocky stream",
                "scholar's garden, "
                "bamboo, "
                "stream, moon",
                "autumn forest, "
                "stream, "
                "red maple",
            ],
            "style": [
                "Chinese ink wash stream painting, "
                "in the style of Ma Lin",
                "literati painting, xieyi freehand",
                "Song dynasty stream landscape",
            ],
            "lighting": [
                "sunlight through leaves, "
                "dappled",
                "moonlight, "
                "silver stream",
                "morning mist",
            ],
            "composition": [
                "horizontal handscroll",
                "square album leaf",
                "vertical hanging scroll, lidu",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed",
                "8k uhd, fresh clarity",
            ],
        },
        "spring": {
            "theme": "泉水",
            "subject": [
                "a mountain spring emerging from rock, "
                "clear water, moss",
                "a hot spring, "
                "steam rising, "
                "pine trees",
                "a scholar drinking from a spring, "
                "bamboo cup",
            ],
            "scene": [
                "mountain cliff, spring, "
                "pine trees, "
                "distant peaks",
                "forest clearing, "
                "spring, moss, "
                "deer",
                "bamboo grove, spring, "
                "stone lantern",
            ],
            "style": [
                "Chinese ink wash spring painting, "
                "in the style of Liang Kai",
                "literati painting, xieyi freehand",
                "Song dynasty spring landscape",
            ],
            "lighting": [
                "sunlight through trees",
                "moonlight, "
                "silver spring",
                "morning mist",
            ],
            "composition": [
                "square album leaf",
                "vertical hanging scroll, lidu",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed",
                "8k uhd, pure freshness",
            ],
        },
    },

    # ============================================================
    # 气象
    # ============================================================
    "weather": {
        "rain": {
            "theme": "雨",
            "subject": [
                "rainy mountain landscape, "
                "misty peaks, "
                "a lone traveler with umbrella",
                "rain on a lotus pond, "
                "droplets on petals, "
                "dragonflies sheltering",
                "rain in a bamboo grove, "
                "droplets, "
                "wind-swept leaves",
            ],
            "scene": [
                "mountain pass, rain, "
                "mist, distant temple",
                "riverside village, "
                "rain, boats, "
                "stone bridge",
                "scholar's garden, rain, "
                "stone lantern",
            ],
            "style": [
                "Chinese ink wash rain painting, "
                "in the style of Mi Fu",
                "literati painting, xieyi freehand",
                "Song dynasty rain landscape, "
                "atmospheric",
            ],
            "lighting": [
                "soft rainy light, "
                "grey-blue tones",
                "storm light, dramatic",
                "twilight, melancholy",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "traditional Chinese rain painting",
                "8k uhd, atmospheric",
            ],
        },
        "snow": {
            "theme": "雪",
            "subject": [
                "snow-covered mountain, "
                "silent forest, "
                "a lone cottage with smoke",
                "snow falling on a plum tree, "
                "blossoms, "
                "quiet winter",
                "snow on a river, "
                "fisherman, "
                "distant temple",
            ],
            "scene": [
                "mountain forest, snow, "
                "deer tracks, "
                "silent",
                "snow village, "
                "warm light from windows",
                "plum branch in snow, "
                "moon",
            ],
            "style": [
                "Chinese ink wash snow painting, "
                "in the style of Wang Wei",
                "literati painting, xieyi freehand",
                "Song dynasty snow painting",
            ],
            "lighting": [
                "soft snow light, "
                "cool blue",
                "moonlight on snow",
                "warm window light",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "horizontal handscroll",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "traditional Chinese snow painting",
                "8k uhd, silent beauty",
            ],
        },
        "mist": {
            "theme": "雾",
            "subject": [
                "misty mountain valley, "
                "peaks emerging, "
                "atmospheric perspective",
                "mist over a river, "
                "a boat emerging, "
                "willow trees",
                "mist in bamboo grove, "
                "silhouettes, "
                "quiet",
            ],
            "scene": [
                "mountain mist, "
                "layered peaks",
                "river mist, "
                "distant temple",
                "forest mist, "
                "deer",
            ],
            "style": [
                "Chinese ink wash mist painting, "
                "in the style of Mi Fu",
                "literati painting, xieyi freehand, "
                "vast negative space",
                "Song dynasty mist landscape, "
                "atmospheric",
            ],
            "lighting": [
                "soft misty light, "
                "ethereal",
                "sunrise mist, "
                "golden glow",
                "twilight mist, "
                "purple tones",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed",
                "8k uhd, atmospheric depth",
            ],
        },
        "wind": {
            "theme": "风",
            "subject": [
                "wind-swept pines, "
                "dramatic branches, "
                "storm clouds",
                "wind bending bamboo, "
                "leaves scattering, "
                "scholar's garden",
                "wind on a lake, "
                "waves, "
                "sailboats leaning",
            ],
            "scene": [
                "mountain pass, wind, "
                "clouds racing",
                "riverside, wind, "
                "willow branches",
                "autumn forest, wind, "
                "leaves flying",
            ],
            "style": [
                "Chinese ink wash wind painting, "
                "in the style of Ma Yuan",
                "literati painting, xieyi freehand, "
                "expressive brushwork",
                "Song dynasty dramatic landscape",
            ],
            "lighting": [
                "stormy light, dramatic",
                "twilight, wind",
                "sunrise, "
                "wind-swept",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed",
                "8k uhd, dramatic motion",
            ],
        },
        "thunder": {
            "theme": "雷电",
            "subject": [
                "lightning over mountain, "
                "storm, "
                "distant peaks",
                "thunderstorm at sea, "
                "waves, "
                "dramatic sky",
                "lightning striking a lone pine, "
                "dramatic",
            ],
            "scene": [
                "mountain valley, storm, "
                "dramatic sky",
                "ocean storm, "
                "waves, "
                "lightning",
                "dark forest, "
                "lightning, "
                "silhouettes",
            ],
            "style": [
                "Chinese ink wash storm painting, "
                "dramatic",
                "literati painting, xieyi freehand",
                "modern Chinese landscape",
            ],
            "lighting": [
                "lightning flash, "
                "high contrast",
                "stormy sky, "
                "dramatic",
                "twilight, "
                "lightning",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "horizontal handscroll",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed",
                "8k uhd, dramatic power",
            ],
        },
        "rainbow": {
            "theme": "彩虹",
            "subject": [
                "rainbow over mountain valley, "
                "after rain, "
                "fresh atmosphere",
                "rainbow over a lake, "
                "mist, "
                "distant pavilion",
                "rainbow over waterfall, "
                "spray, "
                "dramatic",
            ],
            "scene": [
                "mountain valley, "
                "after rain, "
                "sunshine",
                "lake, "
                "rainbow, "
                "willows",
                "waterfall, "
                "rainbow, "
                "moss",
            ],
            "style": [
                "Chinese ink wash rainbow painting, "
                "atmospheric",
                "literati painting, xieyi freehand",
                "modern Chinese landscape",
            ],
            "lighting": [
                "sunlight after rain, "
                "golden",
                "misty rainbow light",
                "evening, "
                "rainbow",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed",
                "8k uhd, hopeful atmosphere",
            ],
        },
    },

    # ============================================================
    # 四季
    # ============================================================
    "season": {
        "spring": {
            "theme": "春",
            "subject": [
                "spring blossoms, "
                "peach and plum, "
                "butterflies, "
                "a stream",
                "spring rain, "
                "green willows, "
                "swallows returning",
                "spring garden, "
                "peonies, "
                "a scholar with a book",
            ],
            "scene": [
                "spring mountain, "
                "blossoms, "
                "misty valley",
                "spring river, "
                "willows, "
                "boats",
                "spring garden, "
                "peonies, "
                "scholar",
            ],
            "style": [
                "Chinese ink wash spring painting, "
                "in the style of Wang Wei",
                "gongbi spring painting, "
                "delicate details",
                "literati painting, xieyi freehand",
            ],
            "lighting": [
                "soft spring morning light",
                "spring rain, "
                "atmospheric",
                "warm afternoon",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "traditional Chinese spring painting",
                "8k uhd, delicate warmth",
            ],
        },
        "summer": {
            "theme": "夏",
            "subject": [
                "lotus pond in full bloom, "
                "dragonflies, "
                "a boat",
                "summer mountain, "
                "pine trees, "
                "a waterfall",
                "summer garden, "
                "bamboo, "
                "a fan",
            ],
            "scene": [
                "lotus pond, "
                "summer, "
                "dragonflies",
                "mountain valley, "
                "summer, "
                "waterfall",
                "bamboo grove, "
                "summer, "
                "shade",
            ],
            "style": [
                "Chinese ink wash summer painting, "
                "in the style of Ma Lin",
                "gongbi summer painting, "
                "vibrant green",
                "literati painting, xieyi freehand",
            ],
            "lighting": [
                "bright summer sunlight",
                "afternoon dappled shade",
                "summer rain",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed",
                "8k uhd, vibrant summer",
            ],
        },
        "autumn": {
            "theme": "秋",
            "subject": [
                "autumn maple forest, "
                "red and gold leaves, "
                "a winding path",
                "autumn moon, "
                "geese flying south, "
                "reeds",
                "autumn mountain, "
                "chrysanthemums, "
                "a scholar",
            ],
            "scene": [
                "autumn mountain, "
                "maple forest",
                "autumn river, "
                "reeds, "
                "geese",
                "autumn garden, "
                "chrysanthemums, "
                "rock",
            ],
            "style": [
                "Chinese ink wash autumn painting, "
                "in the style of Wang Meng",
                "literati painting, autumn palette",
                "Song dynasty autumn landscape",
            ],
            "lighting": [
                "soft autumn light, "
                "golden",
                "sunset, "
                "orange-red",
                "moonlight, "
                "silver",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "horizontal handscroll",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed",
                "8k uhd, poetic melancholy",
            ],
        },
        "winter": {
            "theme": "冬",
            "subject": [
                "snow-covered mountain, "
                "a lone cottage, "
                "smoke rising",
                "winter forest, "
                "bare trees, "
                "a frozen stream",
                "winter river, "
                "a fisherman, "
                "distant temple",
            ],
            "scene": [
                "snow mountain, "
                "winter, "
                "silent",
                "snow forest, "
                "deer tracks",
                "frozen lake, "
                "reeds, "
                "moon",
            ],
            "style": [
                "Chinese ink wash winter painting, "
                "in the style of Wang Wei",
                "literati painting, minimal",
                "Song dynasty winter landscape",
            ],
            "lighting": [
                "cold snow light, "
                "blue tones",
                "moonlight on snow",
                "warm window light",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "horizontal handscroll",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed",
                "8k uhd, silent beauty",
            ],
        },
    },

    # ============================================================
    # 果实
    # ============================================================
    "fruit": {
        "peach": {
            "theme": "桃",
            "subject": [
                "ripe peaches on a branch, "
                "delicate pink blush, "
                "leaves",
                "a basket of peaches, "
                "auspicious symbol of longevity",
                "peach blossoms, "
                "spring, "
                "birds",
            ],
            "scene": [
                "peach tree, spring garden, "
                "butterflies",
                "scholar's studio, "
                "peaches in a bowl",
                "mountain slope, "
                "peach grove, "
                "mist",
            ],
            "style": [
                "Chinese ink peach painting, "
                "in the style of Qi Baishi",
                "gongbi fruit painting, "
                "precise details",
                "literati painting, xieyi freehand",
            ],
            "lighting": [
                "soft spring light",
                "afternoon sunlight, "
                "warm",
                "morning, "
                "dewdrops",
            ],
            "composition": [
                "square album leaf",
                "vertical hanging scroll, lidu",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "traditional Chinese fruit painting",
                "8k uhd, auspicious",
            ],
        },
        "plum": {
            "theme": "李",
            "subject": [
                "ripe plums on a branch, "
                "purple-red, "
                "leaves",
                "a bowl of plums, "
                "scholar's studio",
                "plum blossoms, "
                "spring, "
                "moon",
            ],
            "scene": [
                "plum tree, spring garden",
                "scholar's table, "
                "plums, ink stone",
                "moonlit plum tree, "
                "snow",
            ],
            "style": [
                "Chinese ink plum painting, "
                "in the style of Qi Baishi",
                "gongbi fruit painting, "
                "delicate",
                "literati painting, xieyi freehand",
            ],
            "lighting": [
                "soft afternoon light",
                "moonlight, "
                "silver plums",
                "morning light",
            ],
            "composition": [
                "square album leaf",
                "vertical hanging scroll, lidu",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed",
                "8k uhd",
            ],
        },
        "pomegranate": {
            "theme": "石榴",
            "subject": [
                "a pomegranate, "
                "split open, "
                "seeds visible, "
                "auspicious symbol",
                "pomegranates on a branch, "
                "ripe red, "
                "leaves",
                "a basket of pomegranates, "
                "autumn",
            ],
            "scene": [
                "pomegranate tree, "
                "autumn garden",
                "scholar's studio, "
                "pomegranate in a bowl",
                "rocky cliff, "
                "pomegranate, "
                "birds",
            ],
            "style": [
                "Chinese ink fruit painting, "
                "in the style of Qi Baishi",
                "gongbi pomegranate painting",
                "literati painting, xieyi freehand",
            ],
            "lighting": [
                "autumn sunlight, "
                "warm",
                "morning light",
                "moonlight, "
                "silver",
            ],
            "composition": [
                "square album leaf",
                "vertical hanging scroll, lidu",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "auspicious Chinese fruit painting",
                "8k uhd",
            ],
        },
        "persimmon": {
            "theme": "柿子",
            "subject": [
                "ripe persimmons on a branch, "
                "orange-red, "
                "leaves falling, "
                "autumn",
                "a plate of persimmons, "
                "scholar's studio",
                "six persimmons, "
                "minimal composition, "
                "in the style of Mu Qi",
            ],
            "scene": [
                "persimmon tree, autumn, "
                "birds",
                "scholar's table, "
                "persimmons",
                "autumn garden, "
                "persimmons",
            ],
            "style": [
                "Chinese ink persimmon painting, "
                "in the style of Mu Qi and Qi Baishi",
                "minimalist composition, "
                "six persimmons",
                "literati painting, xieyi freehand",
            ],
            "lighting": [
                "autumn sunlight, "
                "warm",
                "morning light",
                "twilight, "
                "orange glow",
            ],
            "composition": [
                "square album leaf",
                "vertical hanging scroll, lidu",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "traditional Chinese persimmon painting",
                "8k uhd, zen simplicity",
            ],
        },
        "grape": {
            "theme": "葡萄",
            "subject": [
                "a cluster of grapes, "
                "purple, "
                "with leaves and vine",
                "grapes on the vine, "
                "trellis, "
                "summer",
                "a basket of grapes, "
                "abundance",
            ],
            "scene": [
                "grape arbor, "
                "summer garden",
                "scholar's studio, "
                "grapes in a bowl",
                "vineyard, "
                "distant mountains",
            ],
            "style": [
                "Chinese ink grape painting, "
                "in the style of Xu Wei",
                "gongbi grape painting, "
                "precise details",
                "literati painting, xieyi freehand",
            ],
            "lighting": [
                "summer sunlight",
                "afternoon, "
                "dappled shade",
                "moonlight, "
                "silver grapes",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square album leaf",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed",
                "8k uhd",
            ],
        },
        "lychee": {
            "theme": "荔枝",
            "subject": [
                "a cluster of lychees, "
                "red, bumpy skin, "
                "with leaves",
                "lychees in a basket, "
                "summer, "
                "fresh",
                "a lychee branch, "
                "birds, "
                "summer",
            ],
            "scene": [
                "lychee tree, "
                "summer, "
                "birds",
                "scholar's studio, "
                "lychees in a bowl",
                "southern China, "
                "lychee grove",
            ],
            "style": [
                "Chinese ink lychee painting, "
                "in the style of Qi Baishi",
                "gongbi lychee painting",
                "literati painting, xieyi freehand",
            ],
            "lighting": [
                "bright summer light",
                "afternoon, "
                "warm",
                "morning, "
                "fresh",
            ],
            "composition": [
                "square album leaf",
                "vertical hanging scroll, lidu",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed",
                "8k uhd, summer freshness",
            ],
        },
    },

    # ============================================================
    # 蔬果
    # ============================================================
    "vegetable": {
        "cabbage": {
            "theme": "白菜",
            "subject": [
                "a Chinese cabbage, "
                "fresh green and white, "
                "with roots",
                "two cabbages, "
                "one large, one small, "
                "minimal composition",
                "cabbages on a table, "
                "everyday life, "
                "warm",
            ],
            "scene": [
                "scholar's studio, "
                "cabbages, ink stone",
                "kitchen garden, "
                "vegetables",
                "autumn market, "
                "cabbages",
            ],
            "style": [
                "Chinese ink vegetable painting, "
                "in the style of Qi Baishi",
                "gongbi vegetable painting",
                "literati painting, xieyi freehand",
            ],
            "lighting": [
                "soft daylight",
                "morning light, "
                "fresh",
                "afternoon, "
                "warm",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square album leaf",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "traditional Chinese vegetable painting",
                "8k uhd",
            ],
        },
        "radish": {
            "theme": "萝卜",
            "subject": [
                "white radishes, "
                "with green leaves, "
                "basket",
                "a single radish, "
                "minimal composition",
                "radishes and cabbage, "
                "everyday life",
            ],
            "scene": [
                "scholar's studio, "
                "radishes, ink",
                "garden, "
                "vegetables, "
                "soil",
                "market, "
                "vegetables",
            ],
            "style": [
                "Chinese ink vegetable painting, "
                "in the style of Qi Baishi",
                "gongbi vegetable painting",
                "literati painting, xieyi freehand",
            ],
            "lighting": [
                "soft daylight",
                "morning light",
                "afternoon, "
                "warm",
            ],
            "composition": [
                "square album leaf",
                "vertical hanging scroll, lidu",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed",
                "8k uhd",
            ],
        },
        "lotus_root": {
            "theme": "莲藕",
            "subject": [
                "fresh lotus roots, "
                "with lotus leaves, "
                "clear pond",
                "sliced lotus root, "
                "patterned, "
                "minimal",
                "lotus roots, "
                "bamboo basket",
            ],
            "scene": [
                "lotus pond, "
                "fresh roots",
                "scholar's table, "
                "lotus root, tea",
                "market, "
                "fresh vegetables",
            ],
            "style": [
                "Chinese ink vegetable painting, "
                "in the style of Qi Baishi",
                "gongbi vegetable painting, "
                "delicate",
                "literati painting, xieyi freehand",
            ],
            "lighting": [
                "soft daylight",
                "morning freshness",
                "afternoon, "
                "warm",
            ],
            "composition": [
                "square album leaf",
                "vertical hanging scroll, lidu",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed",
                "8k uhd",
            ],
        },
        "bamboo_shoot": {
            "theme": "竹笋",
            "subject": [
                "bamboo shoots emerging, "
                "fresh, "
                "with bamboo leaves",
                "a cluster of bamboo shoots, "
                "minimal",
                "bamboo shoots on a table, "
                "spring",
            ],
            "scene": [
                "bamboo grove, "
                "shoots, "
                "spring rain",
                "scholar's studio, "
                "bamboo shoots, tea",
                "mountain, "
                "bamboo, "
                "mist",
            ],
            "style": [
                "Chinese ink vegetable painting, "
                "in the style of Qi Baishi",
                "gongbi vegetable painting",
                "literati painting, xieyi freehand",
            ],
            "lighting": [
                "spring morning light",
                "afternoon, "
                "warm",
                "misty light",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square album leaf",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed",
                "8k uhd, fresh spring",
            ],
        },
        "gourd": {
            "theme": "葫芦",
            "subject": [
                "a bottle gourd on a vine, "
                "with leaves",
                "several gourds hanging, "
                "vine, "
                "summer",
                "a gourd, "
                "auspicious symbol, "
                "with insects",
            ],
            "scene": [
                "gourd trellis, "
                "summer",
                "scholar's studio, "
                "gourd, ink",
                "autumn field, "
                "gourds",
            ],
            "style": [
                "Chinese ink gourd painting, "
                "in the style of Qi Baishi",
                "gongbi gourd painting",
                "literati painting, xieyi freehand",
            ],
            "lighting": [
                "summer sunlight",
                "afternoon, "
                "warm",
                "moonlight, "
                "silver gourd",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square album leaf",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "auspicious Chinese painting",
                "8k uhd",
            ],
        },
    },

    # ============================================================
    # 器物
    # ============================================================
    "object": {
        "porcelain": {
            "theme": "瓷器",
            "subject": [
                "a blue-and-white porcelain vase, "
                "with floral patterns, "
                "on a wooden stand",
                "a set of porcelain cups, "
                "tea ceremony, "
                "minimal",
                "a porcelain brush pot, "
                "with brushes, "
                "scholar's studio",
            ],
            "scene": [
                "scholar's table, "
                "porcelain, ink stone",
                "tea room, "
                "porcelain, bamboo",
                "imperial court, "
                "porcelain display",
            ],
            "style": [
                "Chinese gongbi still life, "
                "precise details, "
                "mineral pigments",
                "literati painting, "
                "elegant minimalism",
                "blue-and-white porcelain aesthetic",
            ],
            "lighting": [
                "soft interior light",
                "afternoon sunlight, "
                "warm",
                "candlelight, "
                "intimate",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square album leaf",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese porcelain still life",
                "8k uhd, refined elegance",
            ],
        },
        "bronze": {
            "theme": "青铜",
            "subject": [
                "an ancient bronze ritual vessel, "
                "with taotie patterns, "
                "patina",
                "bronze mirrors and coins, "
                "archaeological arrangement",
                "a bronze incense burner, "
                "smoke rising, "
                "scholar's studio",
            ],
            "scene": [
                "archaeological site, "
                "bronze vessels",
                "scholar's studio, "
                "bronze, incense",
                "museum display, "
                "bronze collection",
            ],
            "style": [
                "Chinese gongbi painting, "
                "precise details, "
                "texture of bronze and patina",
                "literati painting, "
                "antiquarian aesthetic",
                "archaeological illustration style",
            ],
            "lighting": [
                "museum light, "
                "dramatic",
                "candlelight, "
                "warm",
                "soft daylight",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square album leaf",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "ancient Chinese bronze painting",
                "8k uhd, archaeological precision",
            ],
        },
        "jade": {
            "theme": "玉器",
            "subject": [
                "a carved jade pendant, "
                "translucent green, "
                "dragon motif",
                "a jade bi disc, "
                "ritual symbol, "
                "on silk",
                "jade ornaments, "
                "scholar's collection",
            ],
            "scene": [
                "scholar's studio, "
                "jade, ink",
                "imperial court, "
                "jade display",
                "temple, "
                "jade ritual objects",
            ],
            "style": [
                "Chinese gongbi painting, "
                "precise details, "
                "translucent jade effect",
                "literati painting, "
                "elegant minimalism",
                "imperial collection style",
            ],
            "lighting": [
                "soft interior light, "
                "jade glow",
                "candlelight, "
                "intimate",
                "sunlight, "
                "translucent",
            ],
            "composition": [
                "square album leaf",
                "vertical hanging scroll, lidu",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese jade painting",
                "8k uhd, translucent beauty",
            ],
        },
        "qin": {
            "theme": "琴棋书画",
            "subject": [
                "a guqin on a table, "
                "with incense burner, "
                "scholar's studio",
                "a Go board with stones, "
                "contemplation",
                "a stack of books, "
                "with brush and ink stone",
            ],
            "scene": [
                "scholar's studio, "
                "qin, chess, books, painting",
                "moonlit pavilion, "
                "guqin",
                "scholar's garden, "
                "painting studio",
            ],
            "style": [
                "Chinese gongbi still life, "
                "elegant, "
                "precise details",
                "literati painting, "
                "xieyi freehand",
                "scholar's studio aesthetic",
            ],
            "lighting": [
                "candlelight, "
                "intimate",
                "moonlight, "
                "scholar's studio",
                "morning light, "
                "studio",
            ],
            "composition": [
                "square album leaf",
                "vertical hanging scroll, lidu",
                "horizontal handscroll",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese scholar's studio painting",
                "8k uhd, refined elegance",
            ],
        },
        "tea": {
            "theme": "茶具",
            "subject": [
                "a tea ceremony set, "
                "teapot, cups, tea leaves",
                "a scholar drinking tea, "
                "with a book",
                "teapot with steam, "
                "minimal composition",
            ],
            "scene": [
                "tea room, "
                "bamboo, "
                "stone lantern",
                "scholar's studio, "
                "tea, books",
                "garden, "
                "tea table, "
                "plum blossoms",
            ],
            "style": [
                "Chinese gongbi still life, "
                "elegant",
                "literati painting, "
                "xieyi freehand",
                "zen tea aesthetic",
            ],
            "lighting": [
                "soft interior light",
                "afternoon sunlight",
                "morning light",
            ],
            "composition": [
                "square album leaf",
                "vertical hanging scroll, lidu",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese tea ceremony painting",
                "8k uhd, zen elegance",
            ],
        },
        "incense": {
            "theme": "香炉",
            "subject": [
                "a bronze incense burner, "
                "with smoke rising, "
                "scholar's studio",
                "an incense burner on a table, "
                "with incense sticks",
                "a celadon incense burner, "
                "smoke, "
                "meditation",
            ],
            "scene": [
                "scholar's studio, "
                "incense, books",
                "temple, "
                "incense, Buddha",
                "meditation room, "
                "incense, cushion",
            ],
            "style": [
                "Chinese gongbi still life",
                "literati painting, "
                "minimal",
                "zen aesthetic",
            ],
            "lighting": [
                "soft interior light",
                "candlelight, "
                "intimate",
                "morning light",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square album leaf",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed",
                "8k uhd, meditative atmosphere",
            ],
        },
    },

    # ============================================================
    # 乐舞
    # ============================================================
    "music": {
        "pipa": {
            "theme": "琵琶",
            "subject": [
                "a lady playing the pipa, "
                "pear-shaped lute, "
                "elegant posture",
                "flying apsara playing pipa, "
                "reversed pipa pose, "
                "Dunhuang mural",
                "a scholar playing pipa, "
                "in a garden, "
                "moonlit",
            ],
            "scene": [
                "palace, "
                "lanterns, "
                "banquet",
                "Dunhuang cave, "
                "Buddhist paradise",
                "garden, "
                "moon, "
                "pavilion",
            ],
            "style": [
                "Tang dynasty court painting, "
                "flowing drapery lines",
                "gongbi figure painting, "
                "mineral pigments",
                "Dunhuang mural style",
            ],
            "lighting": [
                "lantern light, "
                "warm",
                "moonlight, "
                "silver",
                "celestial radiance",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square album leaf",
                "horizontal handscroll",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Tang dynasty music painting",
                "8k uhd, celestial music",
            ],
        },
        "guqin": {
            "theme": "古琴",
            "subject": [
                "a scholar playing the guqin, "
                "seven-stringed zither, "
                "contemplative",
                "a guqin on a table, "
                "incense, "
                "scholar's studio",
                "moonlit guqin, "
                "pine tree, "
                "waterfall",
            ],
            "scene": [
                "scholar's studio, "
                "guqin, books",
                "moonlit pavilion, "
                "guqin",
                "mountain stream, "
                "pine, "
                "guqin",
            ],
            "style": [
                "Chinese gongbi figure painting",
                "literati painting, "
                "xieyi freehand",
                "scholar's studio aesthetic",
            ],
            "lighting": [
                "candlelight, "
                "intimate",
                "moonlight, "
                "silver",
                "morning light",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square album leaf",
                "horizontal handscroll",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese guqin painting",
                "8k uhd, refined elegance",
            ],
        },
        "flute": {
            "theme": "笛",
            "subject": [
                "a shepherd boy playing a bamboo flute, "
                "on a water buffalo",
                "a lady playing the dizi, "
                "bamboo flute, "
                "in a garden",
                "a scholar playing the flute, "
                "moonlit pavilion",
            ],
            "scene": [
                "rice field, "
                "water buffalo, "
                "distant village",
                "garden, "
                "plum blossoms, "
                "moon",
                "mountain stream, "
                "pine, "
                "moonlit",
            ],
            "style": [
                "Chinese gongbi figure painting",
                "literati painting, "
                "xieyi freehand",
                "folk painting style",
            ],
            "lighting": [
                "moonlight, "
                "silver",
                "afternoon sunlight",
                "morning light",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed",
                "8k uhd, pastoral atmosphere",
            ],
        },
        "dance": {
            "theme": "舞",
            "subject": [
                "a court dancer in flowing robes, "
                "long silk sleeves, "
                "graceful movement",
                "a flying apsara dancing, "
                "long ribbons, "
                "Dunhuang mural",
                "a folk dancer, "
                "festival, "
                "lanterns",
            ],
            "scene": [
                "imperial palace, "
                "lanterns, "
                "banquet",
                "Dunhuang cave, "
                "Buddhist paradise",
                "moonlit garden, "
                "pavilion, "
                "peonies",
            ],
            "style": [
                "Tang dynasty court painting, "
                "flowing drapery lines",
                "gongbi figure painting, "
                "mineral pigments",
                "Dunhuang mural style",
            ],
            "lighting": [
                "lantern light, "
                "warm",
                "moonlight, "
                "silver",
                "celestial radiance",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square album leaf",
                "horizontal handscroll",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Tang dynasty dance painting",
                "8k uhd, celestial dance",
            ],
        },
        "bells": {
            "theme": "编钟",
            "subject": [
                "ancient bronze bells, "
                "arranged in a rack, "
                "ritual music",
                "a bronze bell, "
                "with patterns, "
                "archaeological",
                "a monk ringing a temple bell, "
                "misty morning",
            ],
            "scene": [
                "ancient temple, "
                "bells, "
                "incense",
                "archaeological site, "
                "bronze bells",
                "mountain temple, "
                "bell tower, "
                "mist",
            ],
            "style": [
                "Chinese gongbi painting, "
                "precise details",
                "literati painting, "
                "atmospheric",
                "archaeological illustration",
            ],
            "lighting": [
                "museum light, "
                "dramatic",
                "morning mist",
                "candlelight, "
                "temple",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese ritual music painting",
                "8k uhd, ancient atmosphere",
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