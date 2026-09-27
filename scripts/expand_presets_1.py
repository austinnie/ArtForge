# scripts/expand_presets_2b.py
"""
第二批扩展：花、鸟、虫、鱼、兽、猫、狗
共 7 类 42 个预设
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
    # 花
    # ============================================================
    "flower": {
        "plum_blossom": {
            "theme": "梅花",
            "subject": [
                "a branch of plum blossoms, "
                "five petals, "
                "ink outline",
                "an old plum tree, "
                "gnarled branches, "
                "blossoms in snow",
                "a scholar admiring plum blossoms, "
                "with a wine cup, "
                "in a garden",
            ],
            "scene": [
                "snowy garden, "
                "moon, "
                "plum tree",
                "mountain cliff, "
                "mist, "
                "plum blossoms",
                "scholar's studio, "
                "window, "
                "plum branch",
            ],
            "style": [
                "Chinese ink wash painting, "
                "in the style of Wang Mian",
                "literati painting, xieyi freehand",
                "gongbi details, delicate petals",
            ],
            "lighting": [
                "moonlight, silver",
                "snow light, cold",
                "dawn light, soft",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square album leaf",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese plum blossom painting",
                "8k uhd, refined elegance",
            ],
        },
        "orchid": {
            "theme": "兰花",
            "subject": [
                "an orchid, "
                "flowing leaves, "
                "delicate flowers",
                "an orchid in a pot, "
                "with rocks, "
                "on a table",
                "a scholar admiring an orchid, "
                "in a studio",
            ],
            "scene": [
                "scholar's studio, "
                "books, "
                "ink stone",
                "mountain stream, "
                "rocks, "
                "orchid",
                "garden, "
                "bamboo, "
                "orchid",
            ],
            "style": [
                "Chinese ink wash painting, "
                "in the style of Zheng Sixiao",
                "literati painting, xieyi freehand",
                "gongbi details, delicate leaves",
            ],
            "lighting": [
                "soft daylight",
                "morning light, fresh",
                "moonlight, silver",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square album leaf",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese orchid painting",
                "8k uhd, refined elegance",
            ],
        },
        "bamboo": {
            "theme": "竹",
            "subject": [
                "a bamboo grove, "
                "stems and leaves, "
                "ink wash",
                "a single bamboo, "
                "with leaves, "
                "in the wind",
                "a scholar walking in a bamboo grove",
            ],
            "scene": [
                "bamboo grove, "
                "mist, "
                "rocks",
                "mountain slope, "
                "bamboo, "
                "stream",
                "scholar's garden, "
                "bamboo, "
                "stone",
            ],
            "style": [
                "Chinese ink wash painting, "
                "in the style of Wen Tong",
                "literati painting, xieyi freehand",
                "gongbi details, precise leaves",
            ],
            "lighting": [
                "soft misty light",
                "moonlight, silver",
                "morning light, fresh",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "horizontal handscroll",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese bamboo painting",
                "8k uhd, refined elegance",
            ],
        },
        "chrysanthemum": {
            "theme": "菊花",
            "subject": [
                "a chrysanthemum, "
                "many petals, "
                "in full bloom",
                "a cluster of chrysanthemums, "
                "with rocks, "
                "in a garden",
                "a scholar admiring chrysanthemums, "
                "with wine",
            ],
            "scene": [
                "autumn garden, "
                "rocks, "
                "chrysanthemum",
                "scholar's studio, "
                "window, "
                "chrysanthemum",
                "mountain slope, "
                "mist, "
                "chrysanthemum",
            ],
            "style": [
                "Chinese gongbi painting, "
                "precise petals, "
                "in the style of Yun Shouping",
                "literati painting, xieyi freehand",
                "gongbi details, delicate colors",
            ],
            "lighting": [
                "autumn light, warm",
                "afternoon, dappled",
                "moonlight, silver",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square album leaf",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese chrysanthemum painting",
                "8k uhd, refined elegance",
            ],
        },
        "peony": {
            "theme": "牡丹",
            "subject": [
                "a peony, "
                "many petals, "
                "in full bloom",
                "a cluster of peonies, "
                "with rocks, "
                "in a garden",
                "a lady admiring peonies, "
                "in a garden",
            ],
            "scene": [
                "imperial garden, "
                "peonies, "
                "marble balustrade",
                "palace hall, "
                "screens, "
                "peonies in a vase",
                "garden, "
                "peonies, "
                "stone path",
            ],
            "style": [
                "Tang dynasty court painting, "
                "in the style of Zhou Fang",
                "gongbi beauty painting, "
                "fine-line drawing, color washes",
                "gongbi details, rich colors",
            ],
            "lighting": [
                "soft warm daylight",
                "candlelight, intimate",
                "afternoon, warm",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square album leaf",
                "horizontal handscroll",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese peony painting",
                "8k uhd, imperial splendor",
            ],
        },
        "lotus": {
            "theme": "荷花",
            "subject": [
                "a lotus, "
                "pink petals, "
                "large leaves",
                "a lotus pond, "
                "with dragonflies, "
                "in summer",
                "a lady in a boat, "
                "picking lotus",
            ],
            "scene": [
                "lotus pond, "
                "summer, "
                "dragonflies",
                "lake, "
                "lotus, "
                "mist",
                "garden pond, "
                "lotus, "
                "stone bridge",
            ],
            "style": [
                "Chinese gongbi painting, "
                "precise petals, "
                "in the style of Yun Shouping",
                "literati painting, xieyi freehand",
                "gongbi details, delicate colors",
            ],
            "lighting": [
                "summer sunlight, warm",
                "morning light, fresh",
                "moonlight, silver",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese lotus painting",
                "8k uhd, refined elegance",
            ],
        },
    },

    # ============================================================
    # 鸟
    # ============================================================
    "bird": {
        "crane": {
            "theme": "鹤",
            "subject": [
                "a red-crowned crane, "
                "long legs, "
                "white plumage",
                "a pair of cranes, "
                "in a pine tree, "
                "with clouds",
                "a crane flying, "
                "with auspicious clouds",
            ],
            "scene": [
                "pine tree, "
                "clouds, "
                "mountain",
                "lotus pond, "
                "reeds, "
                "mist",
                "celestial palace, "
                "jade terraces, "
                "clouds",
            ],
            "style": [
                "Chinese gongbi painting, "
                "precise feathers, "
                "in the style of Emperor Huizong",
                "literati painting, xieyi freehand",
                "gongbi details, delicate colors",
            ],
            "lighting": [
                "soft misty light",
                "moonlight, silver",
                "dawn light, dreamy",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square album leaf",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese crane painting",
                "8k uhd, refined elegance",
            ],
        },
        "eagle": {
            "theme": "鹰",
            "subject": [
                "an eagle, "
                "spread wings, "
                "sharp talons",
                "an eagle perched on a rock, "
                "with pine, "
                "in a mountain",
                "an eagle flying, "
                "with clouds",
            ],
            "scene": [
                "mountain cliff, "
                "pine, "
                "clouds",
                "steppe, "
                "grassland, "
                "sky",
                "mountain peak, "
                "snow, "
                "sky",
            ],
            "style": [
                "Chinese ink wash painting, "
                "in the style of Lin Liang",
                "literati painting, xieyi freehand",
                "gongbi details, precise feathers",
            ],
            "lighting": [
                "dramatic light",
                "sunset, golden",
                "storm light",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "horizontal handscroll",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese eagle painting",
                "8k uhd, heroic atmosphere",
            ],
        },
        "sparrow": {
            "theme": "麻雀",
            "subject": [
                "a sparrow, "
                "small and lively, "
                "on a branch",
                "a group of sparrows, "
                "on a bamboo branch, "
                "in winter",
                "sparrows, "
                "with rice stalks, "
                "in a field",
            ],
            "scene": [
                "bamboo grove, "
                "winter, "
                "snow",
                "rice field, "
                "autumn, "
                "stooks",
                "garden, "
                "branch, "
                "flowers",
            ],
            "style": [
                "Chinese gongbi painting, "
                "precise feathers, "
                "in the style of Cui Bai",
                "literati painting, xieyi freehand",
                "gongbi details, delicate colors",
            ],
            "lighting": [
                "soft daylight",
                "winter light, cold",
                "morning light, fresh",
            ],
            "composition": [
                "square album leaf",
                "vertical hanging scroll, lidu",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese sparrow painting",
                "8k uhd, refined elegance",
            ],
        },
        "phoenix": {
            "theme": "凤凰",
            "subject": [
                "a phoenix, "
                "colorful plumage, "
                "long tail feathers",
                "a pair of phoenixes, "
                "with peonies, "
                "in a garden",
                "a phoenix flying, "
                "with auspicious clouds",
            ],
            "scene": [
                "celestial palace, "
                "jade terraces, "
                "clouds",
                "imperial garden, "
                "peonies, "
                "marble balustrade",
                "mountain peak, "
                "clouds, "
                "sunrise",
            ],
            "style": [
                "Chinese gongbi painting, "
                "precise feathers, "
                "in the style of Emperor Huizong",
                "gongbi details, rich colors",
                "imperial Chinese painting",
            ],
            "lighting": [
                "celestial radiance, golden",
                "sunrise, warm",
                "imperial radiance, golden",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square album leaf",
                "horizontal handscroll",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese phoenix painting",
                "8k uhd, imperial splendor",
            ],
        },
        "mandarin_duck": {
            "theme": "鸳鸯",
            "subject": [
                "a pair of mandarin ducks, "
                "colorful plumage, "
                "in a pond",
                "mandarin ducks, "
                "with lotus, "
                "in a pond",
                "mandarin ducks, "
                "with reeds, "
                "in autumn",
            ],
            "scene": [
                "lotus pond, "
                "summer, "
                "dragonflies",
                "lake, "
                "reeds, "
                "mist",
                "garden pond, "
                "lotus, "
                "stone bridge",
            ],
            "style": [
                "Chinese gongbi painting, "
                "precise feathers, "
                "in the style of Emperor Huizong",
                "literati painting, xieyi freehand",
                "gongbi details, delicate colors",
            ],
            "lighting": [
                "soft daylight",
                "morning light, fresh",
                "moonlight, silver",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese mandarin duck painting",
                "8k uhd, refined elegance",
            ],
        },
        "swallow": {
            "theme": "燕子",
            "subject": [
                "a swallow, "
                "forked tail, "
                "in flight",
                "a pair of swallows, "
                "with willow, "
                "in spring",
                "swallows, "
                "with peach blossoms, "
                "in a garden",
            ],
            "scene": [
                "willow trees, "
                "spring, "
                "stream",
                "garden, "
                "peach blossoms, "
                "stone path",
                "courtyard, "
                "eaves, "
                "spring",
            ],
            "style": [
                "Chinese gongbi painting, "
                "precise feathers, "
                "in the style of Cui Bai",
                "literati painting, xieyi freehand",
                "gongbi details, delicate colors",
            ],
            "lighting": [
                "spring light, warm",
                "morning light, fresh",
                "afternoon, dappled",
            ],
            "composition": [
                "horizontal handscroll",
                "square album leaf",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese swallow painting",
                "8k uhd, refined elegance",
            ],
        },
    },

    # ============================================================
    # 虫
    # ============================================================
    "insect": {
        "butterfly": {
            "theme": "蝴蝶",
            "subject": [
                "a butterfly, "
                "colorful wings, "
                "on a flower",
                "a group of butterflies, "
                "with peonies, "
                "in a garden",
                "a butterfly, "
                "with plum blossoms, "
                "in spring",
            ],
            "scene": [
                "garden, "
                "peonies, "
                "butterflies",
                "plum tree, "
                "spring, "
                "butterflies",
                "mountain slope, "
                "wild flowers, "
                "butterflies",
            ],
            "style": [
                "Chinese gongbi painting, "
                "precise wings, "
                "in the style of Emperor Huizong",
                "literati painting, xieyi freehand",
                "gongbi details, delicate colors",
            ],
            "lighting": [
                "spring light, warm",
                "morning light, fresh",
                "afternoon, dappled",
            ],
            "composition": [
                "square album leaf",
                "vertical hanging scroll, lidu",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese butterfly painting",
                "8k uhd, refined elegance",
            ],
        },
        "cicada": {
            "theme": "蝉",
            "subject": [
                "a cicada, "
                "translucent wings, "
                "on a branch",
                "a cicada, "
                "with willow, "
                "in summer",
                "a cicada, "
                "with bamboo, "
                "in a garden",
            ],
            "scene": [
                "willow trees, "
                "summer, "
                "stream",
                "bamboo grove, "
                "summer, "
                "shade",
                "garden, "
                "branch, "
                "summer",
            ],
            "style": [
                "Chinese gongbi painting, "
                "precise wings, "
                "in the style of Qi Baishi",
                "literati painting, xieyi freehand",
                "gongbi details, delicate colors",
            ],
            "lighting": [
                "summer sunlight, warm",
                "morning light, fresh",
                "afternoon, dappled",
            ],
            "composition": [
                "square album leaf",
                "vertical hanging scroll, lidu",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese cicada painting",
                "8k uhd, refined elegance",
            ],
        },
        "dragonfly": {
            "theme": "蜻蜓",
            "subject": [
                "a dragonfly, "
                "translucent wings, "
                "on a lotus",
                "a dragonfly, "
                "with lotus, "
                "in a pond",
                "a dragonfly, "
                "with reeds, "
                "in autumn",
            ],
            "scene": [
                "lotus pond, "
                "summer, "
                "dragonflies",
                "lake, "
                "reeds, "
                "mist",
                "garden pond, "
                "lotus, "
                "stone bridge",
            ],
            "style": [
                "Chinese gongbi painting, "
                "precise wings, "
                "in the style of Qi Baishi",
                "literati painting, xieyi freehand",
                "gongbi details, delicate colors",
            ],
            "lighting": [
                "summer sunlight, warm",
                "morning light, fresh",
                "moonlight, silver",
            ],
            "composition": [
                "horizontal handscroll",
                "square album leaf",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese dragonfly painting",
                "8k uhd, refined elegance",
            ],
        },
        "cricket": {
            "theme": "蟋蟀",
            "subject": [
                "a cricket, "
                "on a rock, "
                "with grass",
                "a cricket, "
                "with chrysanthemum, "
                "in autumn",
                "a cricket, "
                "in a jar, "
                "on a table",
            ],
            "scene": [
                "autumn garden, "
                "rocks, "
                "chrysanthemum",
                "scholar's studio, "
                "window, "
                "cricket",
                "mountain slope, "
                "grass, "
                "autumn",
            ],
            "style": [
                "Chinese gongbi painting, "
                "precise details, "
                "in the style of Qi Baishi",
                "literati painting, xieyi freehand",
                "gongbi details, delicate colors",
            ],
            "lighting": [
                "autumn light, warm",
                "moonlight, silver",
                "candlelight, warm",
            ],
            "composition": [
                "square album leaf",
                "vertical hanging scroll, lidu",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese cricket painting",
                "8k uhd, refined elegance",
            ],
        },
        "mantis": {
            "theme": "螳螂",
            "subject": [
                "a mantis, "
                "on a branch, "
                "with leaves",
                "a mantis, "
                "with bamboo, "
                "in a garden",
                "a mantis, "
                "with grass, "
                "in autumn",
            ],
            "scene": [
                "bamboo grove, "
                "summer, "
                "shade",
                "garden, "
                "branch, "
                "summer",
                "mountain slope, "
                "grass, "
                "autumn",
            ],
            "style": [
                "Chinese gongbi painting, "
                "precise details, "
                "in the style of Qi Baishi",
                "literati painting, xieyi freehand",
                "gongbi details, delicate colors",
            ],
            "lighting": [
                "summer sunlight, warm",
                "morning light, fresh",
                "autumn light, warm",
            ],
            "composition": [
                "square album leaf",
                "vertical hanging scroll, lidu",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese mantis painting",
                "8k uhd, refined elegance",
            ],
        },
        "firefly": {
            "theme": "萤火虫",
            "subject": [
                "fireflies, "
                "glowing, "
                "in a garden",
                "a child catching fireflies, "
                "with a fan, "
                "in a garden",
                "fireflies, "
                "with bamboo, "
                "at night",
            ],
            "scene": [
                "garden, "
                "night, "
                "fireflies",
                "bamboo grove, "
                "night, "
                "fireflies",
                "mountain stream, "
                "night, "
                "fireflies",
            ],
            "style": [
                "Chinese gongbi painting, "
                "precise details, "
                "in the style of Qi Baishi",
                "literati painting, xieyi freehand",
                "gongbi details, glowing accents",
            ],
            "lighting": [
                "moonlight, silver",
                "firefly glow, warm",
                "night light, soft",
            ],
            "composition": [
                "horizontal handscroll",
                "square album leaf",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese firefly painting",
                "8k uhd, magical atmosphere",
            ],
        },
    },

    # ============================================================
    # 鱼
    # ============================================================
    "fish": {
        "koi": {
            "theme": "锦鲤",
            "subject": [
                "a koi fish, "
                "colorful scales, "
                "swimming",
                "a group of koi, "
                "in a pond, "
                "with lotus",
                "a koi, "
                "with water ripples, "
                "in a pond",
            ],
            "scene": [
                "lotus pond, "
                "summer, "
                "dragonflies",
                "garden pond, "
                "lotus, "
                "stone bridge",
                "lake, "
                "lotus, "
                "mist",
            ],
            "style": [
                "Chinese gongbi painting, "
                "precise scales, "
                "in the style of Qi Baishi",
                "literati painting, xieyi freehand",
                "gongbi details, delicate colors",
            ],
            "lighting": [
                "summer sunlight, warm",
                "morning light, fresh",
                "moonlight, silver",
            ],
            "composition": [
                "horizontal handscroll",
                "square album leaf",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese koi painting",
                "8k uhd, refined elegance",
            ],
        },
        "goldfish": {
            "theme": "金鱼",
            "subject": [
                "a goldfish, "
                "flowing fins, "
                "swimming",
                "a group of goldfish, "
                "in a bowl, "
                "with water plants",
                "a goldfish, "
                "with water ripples, "
                "in a bowl",
            ],
            "scene": [
                "scholar's studio, "
                "fish bowl, "
                "books",
                "garden, "
                "fish bowl, "
                "stone",
                "tea room, "
                "fish bowl, "
                "tatami",
            ],
            "style": [
                "Chinese gongbi painting, "
                "precise scales, "
                "in the style of Qi Baishi",
                "literati painting, xieyi freehand",
                "gongbi details, delicate colors",
            ],
            "lighting": [
                "soft interior light",
                "morning light, fresh",
                "afternoon, dappled",
            ],
            "composition": [
                "square album leaf",
                "vertical hanging scroll, lidu",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese goldfish painting",
                "8k uhd, refined elegance",
            ],
        },
        "carp": {
            "theme": "鲤鱼",
            "subject": [
                "a carp, "
                "large scales, "
                "swimming",
                "a carp leaping, "
                "with water splashes, "
                "at a waterfall",
                "a group of carp, "
                "in a river, "
                "with reeds",
            ],
            "scene": [
                "river, "
                "reeds, "
                "mist",
                "waterfall, "
                "cliff, "
                "clouds",
                "lake, "
                "lotus, "
                "mist",
            ],
            "style": [
                "Chinese gongbi painting, "
                "precise scales, "
                "in the style of Qi Baishi",
                "literati painting, xieyi freehand",
                "gongbi details, delicate colors",
            ],
            "lighting": [
                "morning light, fresh",
                "sunset, golden",
                "moonlight, silver",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese carp painting",
                "8k uhd, refined elegance",
            ],
        },
        "mandarin_fish": {
            "theme": "鳜鱼",
            "subject": [
                "a mandarin fish, "
                "patterned scales, "
                "swimming",
                "a mandarin fish, "
                "with lotus, "
                "in a pond",
                "a group of mandarin fish, "
                "in a river, "
                "with reeds",
            ],
            "scene": [
                "river, "
                "reeds, "
                "mist",
                "lotus pond, "
                "summer, "
                "dragonflies",
                "lake, "
                "lotus, "
                "mist",
            ],
            "style": [
                "Chinese ink wash painting, "
                "in the style of Bada Shanren",
                "literati painting, xieyi freehand",
                "gongbi details, precise scales",
            ],
            "lighting": [
                "morning light, fresh",
                "moonlight, silver",
                "afternoon, dappled",
            ],
            "composition": [
                "horizontal handscroll",
                "square album leaf",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese mandarin fish painting",
                "8k uhd, refined elegance",
            ],
        },
        "shrimp": {
            "theme": "虾",
            "subject": [
                "a shrimp, "
                "translucent body, "
                "swimming",
                "a group of shrimp, "
                "in a pond, "
                "with water plants",
                "a shrimp, "
                "with water ripples, "
                "in a pond",
            ],
            "scene": [
                "pond, "
                "water plants, "
                "rocks",
                "river, "
                "reeds, "
                "mist",
                "lake, "
                "lotus, "
                "mist",
            ],
            "style": [
                "Chinese ink wash painting, "
                "in the style of Qi Baishi",
                "literati painting, xieyi freehand",
                "gongbi details, translucent body",
            ],
            "lighting": [
                "soft daylight",
                "morning light, fresh",
                "moonlight, silver",
            ],
            "composition": [
                "horizontal handscroll",
                "square album leaf",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese shrimp painting",
                "8k uhd, refined elegance",
            ],
        },
        "crab": {
            "theme": "蟹",
            "subject": [
                "a crab, "
                "claws and shell, "
                "on a rock",
                "a group of crabs, "
                "on a riverbank, "
                "with reeds",
                "a crab, "
                "with chrysanthemum, "
                "in autumn",
            ],
            "scene": [
                "riverbank, "
                "reeds, "
                "autumn",
                "autumn garden, "
                "rocks, "
                "chrysanthemum",
                "market, "
                "crabs, "
                "baskets",
            ],
            "style": [
                "Chinese ink wash painting, "
                "in the style of Qi Baishi",
                "literati painting, xieyi freehand",
                "gongbi details, precise claws",
            ],
            "lighting": [
                "autumn light, warm",
                "morning light, fresh",
                "moonlight, silver",
            ],
            "composition": [
                "horizontal handscroll",
                "square album leaf",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese crab painting",
                "8k uhd, refined elegance",
            ],
        },
    },

    # ============================================================
    # 兽
    # ============================================================
    "beast": {
        "tiger": {
            "theme": "虎",
            "subject": [
                "a tiger, "
                "striped fur, "
                "roaring",
                "a tiger walking, "
                "with pine, "
                "in a mountain",
                "a tiger, "
                "with bamboo, "
                "in a forest",
            ],
            "scene": [
                "mountain cliff, "
                "pine, "
                "clouds",
                "forest, "
                "bamboo, "
                "mist",
                "mountain peak, "
                "snow, "
                "sky",
            ],
            "style": [
                "Chinese ink wash painting, "
                "in the style of Zhang Shanzi",
                "literati painting, xieyi freehand",
                "gongbi details, precise stripes",
            ],
            "lighting": [
                "dramatic light",
                "moonlight, silver",
                "storm light",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "horizontal handscroll",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese tiger painting",
                "8k uhd, heroic atmosphere",
            ],
        },
        "lion": {
            "theme": "狮",
            "subject": [
                "a lion, "
                "mane and tail, "
                "roaring",
                "a pair of lions, "
                "with a ball, "
                "in a court",
                "a lion, "
                "with clouds, "
                "in a mountain",
            ],
            "scene": [
                "imperial court, "
                "throne, "
                "attendants",
                "temple, "
                "incense, "
                "ceremony",
                "mountain peak, "
                "clouds, "
                "sunrise",
            ],
            "style": [
                "Chinese gongbi painting, "
                "precise mane, "
                "in the style of Emperor Huizong",
                "gongbi details, rich colors",
                "imperial Chinese painting",
            ],
            "lighting": [
                "imperial radiance, golden",
                "sunrise, warm",
                "candlelight, ceremony",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square album leaf",
                "horizontal handscroll",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese lion painting",
                "8k uhd, imperial splendor",
            ],
        },
        "horse": {
            "theme": "马",
            "subject": [
                "a horse, "
                "flowing mane, "
                "galloping",
                "a group of horses, "
                "in a meadow, "
                "with mountains",
                "a horse, "
                "with a groom, "
                "in a court",
            ],
            "scene": [
                "steppe, "
                "grassland, "
                "horses",
                "meadow, "
                "mountains, "
                "clouds",
                "imperial court, "
                "stables, "
                "attendants",
            ],
            "style": [
                "Chinese gongbi painting, "
                "precise anatomy, "
                "in the style of Zhao Mengfu",
                "literati painting, xieyi freehand",
                "gongbi details, dynamic pose",
            ],
            "lighting": [
                "daylight, warm",
                "sunset, golden",
                "dramatic light",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese horse painting",
                "8k uhd, dynamic elegance",
            ],
        },
        "deer": {
            "theme": "鹿",
            "subject": [
                "a deer, "
                "antlers, "
                "standing in a forest",
                "a pair of deer, "
                "with pine, "
                "in a mountain",
                "a deer, "
                "with lingzhi, "
                "in a forest",
            ],
            "scene": [
                "forest, "
                "pine, "
                "mist",
                "mountain slope, "
                "grass, "
                "clouds",
                "celestial palace, "
                "jade terraces, "
                "clouds",
            ],
            "style": [
                "Chinese gongbi painting, "
                "precise antlers, "
                "in the style of Emperor Huizong",
                "literati painting, xieyi freehand",
                "gongbi details, delicate colors",
            ],
            "lighting": [
                "soft misty light",
                "moonlight, silver",
                "dawn light, dreamy",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square album leaf",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese deer painting",
                "8k uhd, refined elegance",
            ],
        },
        "dragon": {
            "theme": "龙",
            "subject": [
                "a dragon, "
                "scales and claws, "
                "in the clouds",
                "a dragon, "
                "with pearl, "
                "in the sky",
                "a dragon, "
                "with waves, "
                "in the sea",
            ],
            "scene": [
                "cloud sea, "
                "distant peaks, "
                "cranes",
                "sky, "
                "clouds, "
                "sunrise",
                "sea, "
                "waves, "
                "storm",
            ],
            "style": [
                "Chinese gongbi painting, "
                "precise scales, "
                "in the style of Chen Rong",
                "literati painting, xieyi freehand",
                "gongbi details, dynamic pose",
            ],
            "lighting": [
                "dramatic light",
                "storm light",
                "celestial glow",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "horizontal handscroll",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese dragon painting",
                "8k uhd, dynamic grandeur",
            ],
        },
        "qilin": {
            "theme": "麒麟",
            "subject": [
                "a qilin, "
                "scales and hooves, "
                "in a garden",
                "a qilin, "
                "with auspicious clouds, "
                "in the sky",
                "a qilin, "
                "with a child, "
                "in a court",
            ],
            "scene": [
                "celestial palace, "
                "jade terraces, "
                "clouds",
                "imperial garden, "
                "peonies, "
                "marble balustrade",
                "mountain peak, "
                "clouds, "
                "sunrise",
            ],
            "style": [
                "Chinese gongbi painting, "
                "precise scales, "
                "in the style of Emperor Huizong",
                "gongbi details, rich colors",
                "imperial Chinese painting",
            ],
            "lighting": [
                "celestial radiance, golden",
                "sunrise, warm",
                "imperial radiance, golden",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square album leaf",
                "horizontal handscroll",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese qilin painting",
                "8k uhd, auspicious elegance",
            ],
        },
    },

    # ============================================================
    # 猫
    # ============================================================
    "cat": {
        "cat_sitting": {
            "theme": "猫坐",
            "subject": [
                "a cat sitting, "
                "fluffy fur, "
                "looking at the viewer",
                "a cat sitting on a cushion, "
                "with a tea set, "
                "in a studio",
                "a cat sitting, "
                "with a butterfly, "
                "in a garden",
            ],
            "scene": [
                "scholar's studio, "
                "books, "
                "ink stone",
                "tea room, "
                "tatami, "
                "incense",
                "garden, "
                "peonies, "
                "stone path",
            ],
            "style": [
                "Chinese gongbi painting, "
                "precise fur, "
                "in the style of Qi Baishi",
                "literati painting, xieyi freehand",
                "gongbi details, delicate colors",
            ],
            "lighting": [
                "soft interior light",
                "afternoon, dappled",
                "moonlight, silver",
            ],
            "composition": [
                "square album leaf",
                "vertical hanging scroll, lidu",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese cat painting",
                "8k uhd, refined elegance",
            ],
        },
        "cat_playing": {
            "theme": "猫戏",
            "subject": [
                "a cat playing, "
                "with a ball, "
                "in a garden",
                "a kitten playing, "
                "with a butterfly, "
                "in a garden",
                "a cat playing, "
                "with a feather, "
                "in a studio",
            ],
            "scene": [
                "garden, "
                "peonies, "
                "stone path",
                "scholar's studio, "
                "books, "
                "ink stone",
                "courtyard, "
                "lanterns, "
                "flowers",
            ],
            "style": [
                "Chinese gongbi painting, "
                "precise fur, "
                "in the style of Qi Baishi",
                "literati painting, xieyi freehand",
                "gongbi details, delicate colors",
            ],
            "lighting": [
                "spring light, warm",
                "afternoon, dappled",
                "moonlight, silver",
            ],
            "composition": [
                "square album leaf",
                "vertical hanging scroll, lidu",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese cat painting",
                "8k uhd, playful elegance",
            ],
        },
        "cat_sleeping": {
            "theme": "猫眠",
            "subject": [
                "a cat sleeping, "
                "curled up, "
                "on a cushion",
                "a cat sleeping, "
                "with a book, "
                "in a studio",
                "a cat sleeping, "
                "with plum blossoms, "
                "in a garden",
            ],
            "scene": [
                "scholar's studio, "
                "books, "
                "ink stone",
                "tea room, "
                "tatami, "
                "incense",
                "garden, "
                "plum tree, "
                "snow",
            ],
            "style": [
                "Chinese gongbi painting, "
                "precise fur, "
                "in the style of Qi Baishi",
                "literati painting, xieyi freehand",
                "gongbi details, delicate colors",
            ],
            "lighting": [
                "soft interior light",
                "moonlight, silver",
                "winter light, cold",
            ],
            "composition": [
                "square album leaf",
                "vertical hanging scroll, lidu",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese cat painting",
                "8k uhd, serene elegance",
            ],
        },
        "cat_and_flowers": {
            "theme": "猫与花",
            "subject": [
                "a cat, "
                "with peonies, "
                "in a garden",
                "a cat, "
                "with chrysanthemum, "
                "in autumn",
                "a cat, "
                "with lotus, "
                "in a pond",
            ],
            "scene": [
                "garden, "
                "peonies, "
                "stone path",
                "autumn garden, "
                "rocks, "
                "chrysanthemum",
                "lotus pond, "
                "summer, "
                "dragonflies",
            ],
            "style": [
                "Chinese gongbi painting, "
                "precise fur, "
                "in the style of Qi Baishi",
                "literati painting, xieyi freehand",
                "gongbi details, delicate colors",
            ],
            "lighting": [
                "spring light, warm",
                "autumn light, warm",
                "summer sunlight, warm",
            ],
            "composition": [
                "square album leaf",
                "vertical hanging scroll, lidu",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese cat and flower painting",
                "8k uhd, refined elegance",
            ],
        },
        "cat_and_butterfly": {
            "theme": "猫蝶",
            "subject": [
                "a cat, "
                "with a butterfly, "
                "in a garden",
                "a kitten, "
                "with butterflies, "
                "in a garden",
                "a cat, "
                "with peonies and butterflies, "
                "in a garden",
            ],
            "scene": [
                "garden, "
                "peonies, "
                "butterflies",
                "plum tree, "
                "spring, "
                "butterflies",
                "mountain slope, "
                "wild flowers, "
                "butterflies",
            ],
            "style": [
                "Chinese gongbi painting, "
                "precise fur, "
                "in the style of Qi Baishi",
                "literati painting, xieyi freehand",
                "gongbi details, delicate colors",
            ],
            "lighting": [
                "spring light, warm",
                "morning light, fresh",
                "afternoon, dappled",
            ],
            "composition": [
                "square album leaf",
                "vertical hanging scroll, lidu",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese cat and butterfly painting",
                "8k uhd, refined elegance",
            ],
        },
        "cat_and_fish": {
            "theme": "猫与鱼",
            "subject": [
                "a cat, "
                "with a fish, "
                "in a studio",
                "a cat, "
                "with a fish bowl, "
                "in a studio",
                "a cat, "
                "with dried fish, "
                "in a kitchen",
            ],
            "scene": [
                "scholar's studio, "
                "books, "
                "ink stone",
                "kitchen, "
                "fish, "
                "baskets",
                "courtyard, "
                "lanterns, "
                "flowers",
            ],
            "style": [
                "Chinese gongbi painting, "
                "precise fur, "
                "in the style of Qi Baishi",
                "literati painting, xieyi freehand",
                "gongbi details, delicate colors",
            ],
            "lighting": [
                "soft interior light",
                "afternoon, dappled",
                "candlelight, warm",
            ],
            "composition": [
                "square album leaf",
                "vertical hanging scroll, lidu",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese cat and fish painting",
                "8k uhd, playful elegance",
            ],
        },
    },

    # ============================================================
    # 狗
    # ============================================================
    "dog": {
        "dog_sitting": {
            "theme": "犬坐",
            "subject": [
                "a dog sitting, "
                "fluffy fur, "
                "looking at the viewer",
                "a dog sitting on a cushion, "
                "with a tea set, "
                "in a studio",
                "a dog sitting, "
                "with a butterfly, "
                "in a garden",
            ],
            "scene": [
                "scholar's studio, "
                "books, "
                "ink stone",
                "tea room, "
                "tatami, "
                "incense",
                "garden, "
                "peonies, "
                "stone path",
            ],
            "style": [
                "Chinese gongbi painting, "
                "precise fur, "
                "in the style of Qi Baishi",
                "literati painting, xieyi freehand",
                "gongbi details, delicate colors",
            ],
            "lighting": [
                "soft interior light",
                "afternoon, dappled",
                "moonlight, silver",
            ],
            "composition": [
                "square album leaf",
                "vertical hanging scroll, lidu",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese dog painting",
                "8k uhd, refined elegance",
            ],
        },
        "dog_playing": {
            "theme": "犬戏",
            "subject": [
                "a dog playing, "
                "with a ball, "
                "in a garden",
                "a puppy playing, "
                "with a butterfly, "
                "in a garden",
                "a dog playing, "
                "with a feather, "
                "in a studio",
            ],
            "scene": [
                "garden, "
                "peonies, "
                "stone path",
                "scholar's studio, "
                "books, "
                "ink stone",
                "courtyard, "
                "lanterns, "
                "flowers",
            ],
            "style": [
                "Chinese gongbi painting, "
                "precise fur, "
                "in the style of Qi Baishi",
                "literati painting, xieyi freehand",
                "gongbi details, delicate colors",
            ],
            "lighting": [
                "spring light, warm",
                "afternoon, dappled",
                "moonlight, silver",
            ],
            "composition": [
                "square album leaf",
                "vertical hanging scroll, lidu",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese dog painting",
                "8k uhd, playful elegance",
            ],
        },
        "dog_sleeping": {
            "theme": "犬眠",
            "subject": [
                "a dog sleeping, "
                "curled up, "
                "on a cushion",
                "a dog sleeping, "
                "with a book, "
                "in a studio",
                "a dog sleeping, "
                "with plum blossoms, "
                "in a garden",
            ],
            "scene": [
                "scholar's studio, "
                "books, "
                "ink stone",
                "tea room, "
                "tatami, "
                "incense",
                "garden, "
                "plum tree, "
                "snow",
            ],
            "style": [
                "Chinese gongbi painting, "
                "precise fur, "
                "in the style of Qi Baishi",
                "literati painting, xieyi freehand",
                "gongbi details, delicate colors",
            ],
            "lighting": [
                "soft interior light",
                "moonlight, silver",
                "winter light, cold",
            ],
            "composition": [
                "square album leaf",
                "vertical hanging scroll, lidu",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese dog painting",
                "8k uhd, serene elegance",
            ],
        },
        "dog_and_flowers": {
            "theme": "犬与花",
            "subject": [
                "a dog, "
                "with peonies, "
                "in a garden",
                "a dog, "
                "with chrysanthemum, "
                "in autumn",
                "a dog, "
                "with lotus, "
                "in a pond",
            ],
            "scene": [
                "garden, "
                "peonies, "
                "stone path",
                "autumn garden, "
                "rocks, "
                "chrysanthemum",
                "lotus pond, "
                "summer, "
                "dragonflies",
            ],
            "style": [
                "Chinese gongbi painting, "
                "precise fur, "
                "in the style of Qi Baishi",
                "literati painting, xieyi freehand",
                "gongbi details, delicate colors",
            ],
            "lighting": [
                "spring light, warm",
                "autumn light, warm",
                "summer sunlight, warm",
            ],
            "composition": [
                "square album leaf",
                "vertical hanging scroll, lidu",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese dog and flower painting",
                "8k uhd, refined elegance",
            ],
        },
        "dog_and_butterfly": {
            "theme": "犬蝶",
            "subject": [
                "a dog, "
                "with a butterfly, "
                "in a garden",
                "a puppy, "
                "with butterflies, "
                "in a garden",
                "a dog, "
                "with peonies and butterflies, "
                "in a garden",
            ],
            "scene": [
                "garden, "
                "peonies, "
                "butterflies",
                "plum tree, "
                "spring, "
                "butterflies",
                "mountain slope, "
                "wild flowers, "
                "butterflies",
            ],
            "style": [
                "Chinese gongbi painting, "
                "precise fur, "
                "in the style of Qi Baishi",
                "literati painting, xieyi freehand",
                "gongbi details, delicate colors",
            ],
            "lighting": [
                "spring light, warm",
                "morning light, fresh",
                "afternoon, dappled",
            ],
            "composition": [
                "square album leaf",
                "vertical hanging scroll, lidu",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese dog and butterfly painting",
                "8k uhd, refined elegance",
            ],
        },
        "dog_and_fish": {
            "theme": "犬与鱼",
            "subject": [
                "a dog, "
                "with a fish, "
                "in a studio",
                "a dog, "
                "with a fish bowl, "
                "in a studio",
                "a dog, "
                "with dried fish, "
                "in a kitchen",
            ],
            "scene": [
                "scholar's studio, "
                "books, "
                "ink stone",
                "kitchen, "
                "fish, "
                "baskets",
                "courtyard, "
                "lanterns, "
                "flowers",
            ],
            "style": [
                "Chinese gongbi painting, "
                "precise fur, "
                "in the style of Qi Baishi",
                "literati painting, xieyi freehand",
                "gongbi details, delicate colors",
            ],
            "lighting": [
                "soft interior light",
                "afternoon, dappled",
                "candlelight, warm",
            ],
            "composition": [
                "square album leaf",
                "vertical hanging scroll, lidu",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese dog and fish painting",
                "8k uhd, playful elegance",
            ],
        },
    },
}


def main():
    created = 0
    skipped = 0
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
                skipped += 1
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
    print(f"共创建 {created} 个新预设，跳过 {skipped} 个已存在预设")


if __name__ == "__main__":
    main()