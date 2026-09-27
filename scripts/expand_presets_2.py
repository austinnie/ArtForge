# scripts/expand_presets_2.py
"""
第二批：山水、人物、建筑、树木
每个分类 6 个预设
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
    # 山水
    # ============================================================
    "landscape": {
        "shanshui_ink": {
            "theme": "水墨山水",
            "subject": [
                "towering mountain peaks, layered ridges, "
                "misty valleys, a lone pavilion on a cliff",
                "grand mountain range with pine trees, "
                "winding path, distant waterfall",
                "snow-capped peaks, cloud sea, "
                "eagle soaring, silent grandeur",
            ],
            "scene": [
                "misty river valley, floating clouds, "
                "distant temple, faint bell",
                "stormy sky, wind-swept pines, "
                "rocky cliff, waterfall",
                "autumn mountains, red maple, "
                "lonely pavilion, wild geese",
            ],
            "style": [
                "Chinese ink wash landscape, "
                "in the style of Fan Kuan and Guo Xi",
                "literati painting, xieyi freehand, "
                "monochrome ink, vast negative space, "
                "in the style of Mi Fu",
                "Song dynasty monumental landscape, "
                "texture strokes (cunfa), atmospheric perspective",
            ],
            "lighting": [
                "soft misty light, atmospheric depth",
                "dawn light breaking through clouds",
                "twilight, purple-orange sky",
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
        "qinglv_shanshui": {
            "theme": "青绿山水",
            "subject": [
                "grand blue-green mountain range, "
                "mineral pigments, decorative stylized peaks",
                "river valley between peaks, "
                "boats, bridges, travelers",
                "immortal mountain, jade-green peaks, "
                "golden sunlight, auspicious clouds",
            ],
            "scene": [
                "crystal clear river, stone bridge, "
                "willow trees, distant pagoda",
                "clouds and mist between peaks, "
                "waterfall plunging",
                "imperial garden with lakes, "
                "jade-green hills, pavilions",
            ],
            "style": [
                "traditional Chinese blue-green landscape, "
                "mineral pigments, decorative stylized mountains, "
                "in the style of Zhan Ziqian and Zhang Daqian",
                "gongbi landscape, meticulous outlines, "
                "azurite blue and malachite green",
                "Tang dynasty court painting, "
                "gold leaf accents, refined brushwork",
            ],
            "lighting": [
                "golden sunlight on peaks, warm glow",
                "bright noon light, clear atmosphere",
                "sunset, orange-pink glow on peaks",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "traditional Chinese blue-green landscape",
                "8k uhd, brilliant mineral pigments",
            ],
        },
        "snow_landscape": {
            "theme": "雪景山水",
            "subject": [
                "snow-covered mountain peaks, "
                "frozen river, a lone fisherman",
                "winter forest, snow-laden pines, "
                "a small hut with smoking chimney",
                "snowy mountain pass, travelers, "
                "distant temple, twilight",
            ],
            "scene": [
                "frozen lake, snow-covered reeds, "
                "distant mountain, silent winter",
                "snow-covered village, "
                "warm light from windows, "
                "chimney smoke",
                "winter forest, snow-laden branches, "
                "deer tracks, silent atmosphere",
            ],
            "style": [
                "Chinese ink wash snow landscape, "
                "in the style of Wang Wei",
                "Song dynasty snow painting, "
                "subtle white and grey gradations",
                "literati snow painting, xieyi, "
                "vast negative space, minimalist",
            ],
            "lighting": [
                "cold blue light, snow reflection",
                "warm light from window, contrast",
                "moonlight on snow, silver tones",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "horizontal handscroll",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "traditional Chinese snow painting",
                "8k uhd, subtle white gradations",
            ],
        },
        "autumn_mountain": {
            "theme": "秋山",
            "subject": [
                "autumn mountain, red maple leaves, "
                "winding path, a lone traveler",
                "harvest season mountain village, "
                "persimmon trees, distant smoke",
                "autumn river, geese flying south, "
                "withered lotus, melancholy",
            ],
            "scene": [
                "autumn forest, red and yellow leaves, "
                "mountain stream, stone bridge",
                "misty autumn morning, "
                "mountains covered in fog",
                "autumn moon, quiet lake, "
                "reeds, wild geese",
            ],
            "style": [
                "Chinese ink wash, autumn palette, "
                "in the style of Wang Meng",
                "literati painting, xieyi freehand, "
                "autumn colors",
                "Song dynasty autumn painting, "
                "poetic melancholy",
            ],
            "lighting": [
                "soft autumn light, golden tones",
                "twilight, warm orange glow",
                "moonlight, silver on water",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "horizontal handscroll",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "traditional Chinese autumn landscape",
                "8k uhd, poetic atmosphere",
            ],
        },
        "cloud_sea": {
            "theme": "云海",
            "subject": [
                "mountain peaks rising from cloud sea, "
                "sunrise, golden glow on clouds",
                "eagle soaring above cloud sea, "
                "mountain peaks, vast expanse",
                "a pagoda on a peak, "
                "surrounded by clouds, mystical",
            ],
            "scene": [
                "sunrise over cloud sea, "
                "golden and pink clouds",
                "misty morning, peaks like islands, "
                "distant temple bell",
                "sunset cloud sea, purple and orange, "
                "mystical atmosphere",
            ],
            "style": [
                "Chinese ink wash, cloud sea, "
                "in the style of Huang Shan school",
                "literati painting, misty atmosphere",
                "modern Chinese landscape, "
                "in the style of Zhang Daqian",
            ],
            "lighting": [
                "sunrise light, golden glow",
                "moonlight, silver clouds",
                "sunset, dramatic colors",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "traditional Chinese cloud sea painting",
                "8k uhd, ethereal atmosphere",
            ],
        },
        "waterfall_gorge": {
            "theme": "飞瀑深谷",
            "subject": [
                "grand waterfall plunging down cliff, "
                "spray, rainbow, rocky gorge",
                "hidden waterfall in deep valley, "
                "ancient trees, mossy rocks",
                "mountain stream cascading over boulders, "
                "pine trees on cliff",
            ],
            "scene": [
                "deep gorge, rocky cliffs, "
                "pines clinging to rocks",
                "misty valley, waterfall, "
                "distant mountains, atmospheric",
                "spring waterfall, plum blossoms, "
                "scholar contemplating",
            ],
            "style": [
                "Chinese ink wash waterfall, "
                "in the style of Ma Yuan and Xia Gui",
                "Song dynasty landscape, "
                "one-corner composition",
                "literati painting, xieyi freehand",
            ],
            "lighting": [
                "misty light, spray rainbow",
                "morning light on waterfall",
                "twilight, silhouette of cliff",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "horizontal handscroll",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "traditional Chinese waterfall painting",
                "8k uhd, dramatic atmosphere",
            ],
        },
    },

    # ============================================================
    # 人物
    # ============================================================
    "figure": {
        "literati": {
            "theme": "文人",
            "subject": [
                "a Chinese scholar in a long robe, "
                "reading under a pine tree, "
                "serene and contemplative",
                "a literati at his desk, "
                "brushes, ink stone, xuan paper",
                "an elderly scholar contemplating "
                "a scroll of calligraphy",
            ],
            "scene": [
                "scholar's studio, bamboo, "
                "rock garden, quiet atmosphere",
                "pine forest, misty mountain, "
                "a small pavilion",
                "riverside pavilion, lotus pond, "
                "autumn moon",
            ],
            "style": [
                "traditional Chinese figure painting, "
                "in the style of Tang Yin and Wen Zhengming",
                "gongbi figure painting, "
                "elegant brushwork, mineral pigments",
                "literati painting, xieyi freehand",
            ],
            "lighting": [
                "soft afternoon light, warm",
                "moonlight through window",
                "candlelight, warm glow",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square album leaf",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "traditional Chinese figure painting",
                "8k uhd, elegant refinement",
            ],
        },
        "beauty": {
            "theme": "仕女",
            "subject": [
                "a Tang dynasty court lady, plump and elegant, "
                "high-waisted silk robe, holding a round fan, "
                "in the style of Zhou Fang",
                "a beauty in a garden, "
                "surrounded by peonies, delicate",
                "a lady playing a guqin, "
                "elegant posture, silk robe",
            ],
            "scene": [
                "imperial garden, peonies, "
                "marble balustrade, lotus pond",
                "palace interior, screens, "
                "cushions, incense rising",
                "scholar's garden, bamboo, "
                "stone lantern, moon",
            ],
            "style": [
                "Tang dynasty court painting, "
                "in the style of Zhou Fang and Zhang Xuan",
                "gongbi beauty painting, "
                "fine-line drawing, color washes",
                "Ming dynasty beauty painting, "
                "in the style of Tang Yin",
            ],
            "lighting": [
                "soft warm daylight",
                "candlelight, intimate mood",
                "moonlight, silver tones",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square album leaf",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "traditional Chinese beauty painting",
                "8k uhd, delicate beauty",
            ],
        },
        "immortal": {
            "theme": "仙人",
            "subject": [
                "an immortal riding a crane, "
                "flowing robes, transcendent",
                "an immortal sage with long beard, "
                "long staff, mountain peak",
                "the Eight Immortals, "
                "dancing in clouds, celebratory",
            ],
            "scene": [
                "misty mountain peak, "
                "auspicious clouds, cranes",
                "island of immortals, "
                "peach trees, waterfall",
                "jade palace in clouds, "
                "dragon and phoenix",
            ],
            "style": [
                "traditional Chinese immortal painting, "
                "gongbi, mineral pigments",
                "in the style of Wu Daozi, "
                "flowing drapery lines",
                "folk painting style, vibrant colors",
            ],
            "lighting": [
                "celestial radiance, ethereal",
                "dawn light, golden glow",
                "moonlight, silver",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square album leaf",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "traditional Chinese immortal painting",
                "8k uhd",
            ],
        },
        "monk": {
            "theme": "僧人",
            "subject": [
                "a Zen monk in meditation, "
                "shaved head, simple robe, "
                "serene expression",
                "a monk sweeping leaves, "
                "autumn temple, quiet",
                "an old abbot with long eyebrows, "
                "holding a staff",
            ],
            "scene": [
                "mountain temple, stone steps, "
                "ancient pines, mist",
                "Zen garden, raked gravel, "
                "stone, moss",
                "riverside hermitage, "
                "bamboo, moon",
            ],
            "style": [
                "Chinese Chan painting, "
                "in the style of Liang Kai",
                "ink and wash, xieyi, "
                "minimal brushwork",
                "gongbi monk painting, "
                "precise details",
            ],
            "lighting": [
                "soft morning light",
                "twilight, contemplative",
                "candlelight, meditation",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square album leaf",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "traditional Chinese Chan painting",
                "8k uhd, zen atmosphere",
            ],
        },
        "children": {
            "theme": "童子",
            "subject": [
                "a Chinese child with a top-knot, "
                "playing with a butterfly, joyful",
                "two children, one on a water buffalo, "
                "one playing a flute",
                "a child offering peaches, "
                "auspicious symbol",
            ],
            "scene": [
                "garden with peonies, "
                "butterflies, spring",
                "rice field, water buffalo, "
                "distant village",
                "imperial court, "
                "festival, lanterns",
            ],
            "style": [
                "traditional Chinese children painting, "
                "in the style of Song dynasty",
                "gongbi children painting, "
                "fine details, mineral pigments",
                "folk painting, festive",
            ],
            "lighting": [
                "spring morning light, warm",
                "summer sunlight, bright",
                "lantern light, festival",
            ],
            "composition": [
                "square album leaf",
                "round fan",
                "vertical hanging scroll, lidu",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed",
                "8k uhd, joyful atmosphere",
            ],
        },
        "warrior": {
            "theme": "武将",
            "subject": [
                "a Chinese general in armor, "
                "long spear, imposing posture",
                "a warrior with a sword, "
                "flowing robes, martial stance",
                "a mounted warrior, "
                "galloping horse, dynamic",
            ],
            "scene": [
                "mountain pass, banner, "
                "warriors in formation",
                "imperial palace, "
                "audience with the emperor",
                "battlefield, smoke, "
                "distant mountains",
            ],
            "style": [
                "traditional Chinese warrior painting, "
                "gongbi, armor details",
                "in the style of Qing dynasty, "
                "mural painting",
                "folk painting style, "
                "Theater influence",
            ],
            "lighting": [
                "dramatic light, strong shadows",
                "dawn light, heroism",
                "stormy sky, dramatic",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square album leaf",
                "horizontal handscroll",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "traditional Chinese warrior painting",
                "8k uhd, martial spirit",
            ],
        },
    },

    # ============================================================
    # 建筑
    # ============================================================
    "architecture": {
        "palace": {
            "theme": "宫殿",
            "subject": [
                "grand imperial palace, "
                "multi-storied pavilions, "
                "colored glazed roofs",
                "Tang palace hall, "
                "red columns, golden tiles, "
                "imperial audience",
                "Forbidden City, "
                "majestic gate, "
                "cloud-patterned roofs",
            ],
            "scene": [
                "imperial garden, peonies, "
                "marble balustrade, lotus pond",
                "grand courtyard, "
                "stone lions, incense burners",
                "mountain backdrop, "
                "palace in distance",
            ],
            "style": [
                "Tang dynasty architectural painting, "
                "jiehua ruled-line style, "
                "in the style of Li Sixun",
                "gongbi architecture painting, "
                "mineral pigments, precise details",
                "Qing dynasty court painting, "
                "gold leaf accents",
            ],
            "lighting": [
                "bright daylight, golden sunshine",
                "sunset, warm glow on roofs",
                "moonlight, blue-silver palace",
            ],
            "composition": [
                "horizontal handscroll",
                "square album leaf",
                "vertical hanging scroll, lidu",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "traditional Chinese architecture painting",
                "8k uhd, grand architectural details",
            ],
        },
        "temple": {
            "theme": "寺庙",
            "subject": [
                "a Buddhist temple on a mountain cliff, "
                "multi-eaved halls, stone steps",
                "a Chan temple, "
                "bell tower, drum tower, "
                "bamboo grove",
                "a pagoda rising above trees, "
                "misty morning",
            ],
            "scene": [
                "mountain forest, "
                "stone steps, moss, "
                "distant peak",
                "incense smoke rising, "
                "prayer flags, "
                "ancient trees",
                "riverside temple, "
                "stone bridge, moon",
            ],
            "style": [
                "traditional Chinese temple painting, "
                "gongbi, architectural details",
                "in the style of Wang Meng, "
                "dense texture strokes",
                "literati painting, "
                "ink wash, minimalist",
            ],
            "lighting": [
                "morning mist, atmospheric",
                "twilight, warm incense glow",
                "moonlight, silver temple",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "horizontal handscroll",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "traditional Chinese temple painting",
                "8k uhd, spiritual atmosphere",
            ],
        },
        "bridge": {
            "theme": "桥梁",
            "subject": [
                "an arched stone bridge, "
                "reflection in water, "
                "willow trees at each end",
                "a wooden covered bridge, "
                "rain, travelers with umbrellas",
                "a bridge over a mountain stream, "
                "pine trees, wildflowers",
            ],
            "scene": [
                "river valley, stone bridge, "
                "willow trees, distant village",
                "mountain stream, wooden bridge, "
                "rocky banks, moss",
                "canal town, stone bridge, "
                "boats, lanterns at dusk",
            ],
            "style": [
                "traditional Chinese bridge painting, "
                "gongbi, architectural details",
                "ink and wash, xieyi freehand",
                "in the style of Zhang Zeduan, "
                "Qingming Scroll",
            ],
            "lighting": [
                "sunset, warm glow on bridge",
                "rainy day, misty atmosphere",
                "lantern light, evening",
            ],
            "composition": [
                "horizontal handscroll",
                "square album leaf",
                "vertical hanging scroll, lidu",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed",
                "8k uhd, poetic atmosphere",
            ],
        },
        "garden": {
            "theme": "园林",
            "subject": [
                "a Chinese classical garden, "
                "zigzag bridge, rockery, "
                "lotus pond",
                "a scholar's garden, "
                "moon gate, bamboo, "
                "stone lantern",
                "a garden pavilion, "
                "surrounded by plum blossoms, "
                "spring",
            ],
            "scene": [
                "rock garden, winding path, "
                "moss, stone, water",
                "lotus pond, koi fish, "
                "willow tree, moon",
                "bamboo grove, stone path, "
                "window with lattice pattern",
            ],
            "style": [
                "Chinese garden painting, "
                "gongbi, refined details",
                "literati painting, "
                "ink and wash, elegant",
                "in the style of Wen Zhengming, "
                "Suzhou gardens",
            ],
            "lighting": [
                "spring morning light",
                "summer afternoon, dappled shade",
                "moonlight, poetic garden",
            ],
            "composition": [
                "square album leaf",
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "traditional Chinese garden painting",
                "8k uhd, elegant refinement",
            ],
        },
        "village": {
            "theme": "村舍",
            "subject": [
                "a mountain village, "
                "thatched cottages, smoke from chimneys, "
                "distant peaks",
                "a fishing village by the sea, "
                "boats, nets, sunset",
                "a farmhouse in rice fields, "
                "water buffalo, willow trees",
            ],
            "scene": [
                "rice paddies, terraced fields, "
                "mountain backdrop",
                "riverside village, "
                "stone bridge, willow trees",
                "snow-covered village, "
                "warm light from windows",
            ],
            "style": [
                "traditional Chinese village painting, "
                "ink and wash, xieyi",
                "in the style of Qi Baishi, "
                "rural scenes",
                "gongbi, detailed village life",
            ],
            "lighting": [
                "sunrise, golden warmth",
                "sunset, orange glow",
                "snow light, cool blue",
            ],
            "composition": [
                "horizontal handscroll",
                "square album leaf",
                "vertical hanging scroll, lidu",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "traditional Chinese rural painting",
                "8k uhd, peaceful atmosphere",
            ],
        },
        "pagoda": {
            "theme": "宝塔",
            "subject": [
                "a tall multi-storied pagoda, "
                "rising above misty trees",
                "a pagoda on a mountain peak, "
                "surrounded by clouds",
                "a pagoda reflected in a lake, "
                "twilight",
            ],
            "scene": [
                "mountain forest, mist, "
                "stone steps leading to pagoda",
                "lake, reflection of pagoda, "
                "lotus, koi",
                "snow-covered pagoda, "
                "winter, silent",
            ],
            "style": [
                "traditional Chinese pagoda painting, "
                "gongbi, precise architecture",
                "ink and wash, minimalist",
                "literati painting, atmospheric",
            ],
            "lighting": [
                "sunrise light, golden pagoda",
                "twilight, purple-pink sky",
                "moonlight, silver pagoda",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square album leaf",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "traditional Chinese pagoda painting",
                "8k uhd, spiritual atmosphere",
            ],
        },
    },

    # ============================================================
    # 树木
    # ============================================================
    "tree": {
        "pine": {
            "theme": "松",
            "subject": [
                "an ancient pine tree, gnarled branches, "
                "clinging to a rocky cliff",
                "a pair of pine trees, "
                "one straight, one bent, "
                "symbol of fidelity",
                "pine branches with snow, "
                "winter scene, silent",
            ],
            "scene": [
                "rocky cliff, mountain mist, "
                "distant peaks",
                "mountain temple, stone steps, "
                "pine forest",
                "snow-covered mountain, "
                "winter silence",
            ],
            "style": [
                "Chinese ink wash pine painting, "
                "in the style of Li Cheng and Guo Xi",
                "literati painting, xieyi freehand",
                "gongbi pine painting, "
                "precise needles and bark",
            ],
            "lighting": [
                "sunrise light, golden needles",
                "moonlight, silver pine",
                "snow light, cool blue",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "horizontal handscroll",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "traditional Chinese pine painting",
                "8k uhd, resilient spirit",
            ],
        },
        "bamboo": {
            "theme": "竹",
            "subject": [
                "a bamboo grove, tall green stalks, "
                "wind rustling, delicate leaves",
                "a single bamboo stalk, "
                "leaves moving in breeze",
                "bamboo in snow, "
                "winter, resilient",
            ],
            "scene": [
                "scholar's garden, rock, "
                "bamboo, quiet atmosphere",
                "mountain forest, mist, "
                "bamboo, waterfall",
                "moonlit bamboo grove, "
                "silhouettes",
            ],
            "style": [
                "Chinese ink bamboo painting, "
                "in the style of Wen Tong and Zheng Xie",
                "literati painting, xieyi, "
                "expressive brushwork",
                "gongbi bamboo painting, "
                "precise leaves",
            ],
            "lighting": [
                "soft morning light",
                "moonlight through bamboo",
                "wind and rain, dramatic",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "horizontal handscroll",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "traditional Chinese bamboo painting",
                "8k uhd, elegant resilience",
            ],
        },
        "plum_tree": {
            "theme": "梅树",
            "subject": [
                "an ancient plum tree, gnarled trunk, "
                "branches covered with blossoms",
                "a plum branch in snow, "
                "winter, resilient",
                "two plum branches crossing, "
                "yin-yang composition",
            ],
            "scene": [
                "snow-covered mountain, "
                "plum tree, winter",
                "moonlit night, "
                "plum blossoms, window",
                "spring morning, "
                "plum blossoms, birds",
            ],
            "style": [
                "Chinese ink plum painting, "
                "in the style of Wang Mian",
                "literati painting, xieyi freehand",
                "gongbi plum painting, "
                "precise petals",
            ],
            "lighting": [
                "moonlight on snow",
                "spring morning light",
                "twilight, purple sky",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "horizontal handscroll",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "traditional Chinese plum painting",
                "8k uhd, winter resilience",
            ],
        },
        "willow": {
            "theme": "柳",
            "subject": [
                "a weeping willow by a river, "
                "long branches trailing in water",
                "willow trees lining a canal, "
                "boats, spring breeze",
                "willow branches with swallows, "
                "spring scene",
            ],
            "scene": [
                "riverside, spring, "
                "willow trees, distant village",
                "canal town, stone bridge, "
                "willow, boats",
                "lake, weeping willow, "
                "full moon, reflection",
            ],
            "style": [
                "Chinese ink willow painting, "
                "in the style of Ma Yuan",
                "literati painting, xieyi",
                "gongbi willow painting, "
                "precise leaves",
            ],
            "lighting": [
                "spring morning light, warm",
                "afternoon, dappled shade",
                "moonlight, poetic",
            ],
            "composition": [
                "horizontal handscroll",
                "square album leaf",
                "vertical hanging scroll, lidu",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "traditional Chinese willow painting",
                "8k uhd, gentle spring",
            ],
        },
        "maple": {
            "theme": "枫",
            "subject": [
                "a large maple tree, "
                "red and orange leaves, autumn",
                "maple branches overhanging a stream, "
                "leaves falling",
                "maple tree in moonlight, "
                "silhouette, dramatic",
            ],
            "scene": [
                "autumn mountain, "
                "maple forest, winding path",
                "stream, maple leaves, "
                "rock, moss",
                "moonlit maple, "
                "deer, silent",
            ],
            "style": [
                "Chinese ink maple painting, "
                "in the style of Wang Meng",
                "literati painting, autumn palette",
                "gongbi maple painting, "
                "precise leaves",
            ],
            "lighting": [
                "autumn afternoon light, warm",
                "sunset, orange-red glow",
                "moonlight, silver maple",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "horizontal handscroll",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "traditional Chinese maple painting",
                "8k uhd, brilliant autumn colors",
            ],
        },
        "banyan": {
            "theme": "榕树",
            "subject": [
                "a grand banyan tree, "
                "massive trunk, aerial roots",
                "a banyan tree by a river, "
                "fisherman under it",
                "a banyan grove, "
                "shade, birds",
            ],
            "scene": [
                "riverside, banyan, "
                "fisherman, boats",
                "village, banyan, "
                "children playing",
                "mountain, banyan, "
                "mist, birds",
            ],
            "style": [
                "Chinese ink banyan painting, "
                "in the style of Qi Baishi",
                "literati painting, xieyi",
                "gongbi banyan painting, "
                "dense foliage",
            ],
            "lighting": [
                "summer afternoon, dappled shade",
                "sunrise, golden banyan",
                "moonlight, silver banyan",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "traditional Chinese banyan painting",
                "8k uhd, ancient resilience",
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