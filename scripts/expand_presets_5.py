# scripts/expand_presets_5.py
"""
第五批：服饰、戏曲、佛道、医药、民俗、朝代、地域、现代融合
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
    # 服饰
    # ============================================================
    "costume": {
        "hanfu": {
            "theme": "汉服",
            "subject": [
                "a lady in Han dynasty robe, "
                "wide sleeves, "
                "crossed collar, long skirt",
                "a scholar in Hanfu, "
                "with a jade pendant, "
                "bamboo grove",
                "a young lady in flowing hanfu, "
                "long ribbons, "
                "in a garden",
            ],
            "scene": [
                "bamboo grove, spring, "
                "petals falling",
                "scholar's garden, "
                "peonies, stone lantern",
                "riverside, willow trees, "
                "boat"
            ],
            "style": [
                "traditional Chinese figure painting, "
                "gongbi details, mineral pigments",
                "literati painting, xieyi freehand",
                "in the style of Tang Yin",
            ],
            "lighting": [
                "spring morning light, warm",
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
                "Chinese hanfu painting",
                "8k uhd, flowing drapery",
            ],
        },
        "tang_dress": {
            "theme": "唐装",
            "subject": [
                "a Tang dynasty court lady, "
                "plump and elegant, "
                "high-waisted silk robe",
                "a lady with elaborate hairstyle, "
                "golden hairpin, "
                "Tang dynasty",
                "a lady in Tang dress, "
                "holding a round fan, "
                "garden",
            ],
            "scene": [
                "imperial garden, peonies, "
                "marble balustrade, lotus pond",
                "palace interior, screens, "
                "cushions, incense rising",
                "spring garden, cherry blossoms, "
                "stone path",
            ],
            "style": [
                "Tang dynasty court painting, "
                "in the style of Zhou Fang and Zhang Xuan",
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
                "vertical hanging scroll, lidu",
                "square album leaf",
                "horizontal handscroll",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Tang dynasty court lady painting",
                "8k uhd, elegant beauty",
            ],
        },
        "kimono": {
            "theme": "和服",
            "subject": [
                "a Japanese lady in kimono, "
                "delicate patterns, "
                "obi belt, "
                "long flowing sleeves",
                "a maiko in furisode, "
                "colorful silk, "
                "cherry blossoms",
                "a lady in a geisha kimono, "
                "ornate hairpins, "
                "tatami room",
            ],
            "scene": [
                "cherry blossom garden, "
                "stone lantern, koi pond",
                "tatami room, "
                "shoji screens, "
                "afternoon light",
                "Gion street, "
                "lanterns, "
                "evening"
            ],
            "style": [
                "ukiyo-e woodblock print, "
                "flat colors, bold outlines",
                "nihonga, refined brushwork, "
                "mineral pigments",
                "in the style of Kitagawa Utamaro",
            ],
            "lighting": [
                "spring morning light",
                "evening lantern light, warm",
                "moonlight, silver",
            ],
            "composition": [
                "vertical hanging scroll, kakemono",
                "square album leaf",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Japanese kimono painting",
                "8k uhd, refined elegance",
            ],
        },
        "nomad": {
            "theme": "胡服",
            "subject": [
                "a Tang dynasty lady in hufu, "
                "riding clothes, "
                "leather boots, "
                "riding a horse",
                "a man in nomad outfit, "
                "fur hat, "
                "riding a camel",
                "a lady in hufu, "
                "with a bow, "
                "mountain path",
            ],
            "scene": [
                "mountain path, "
                "autumn, "
                "distant peaks",
                "desert, "
                "sand dunes, "
                "sunset",
                "steppe, "
                "grassland, "
                "wild flowers",
            ],
            "style": [
                "Tang dynasty painting, "
                "mineral pigments, precise details",
                "gongbi figure painting",
                "in the style of Zhang Xuan",
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
                "Tang dynasty hufu painting",
                "8k uhd, dynamic elegance",
            ],
        },
        "crown": {
            "theme": "冠冕",
            "subject": [
                "an emperor in ceremonial crown and robe, "
                "dragon pattern, "
                "imperial dignity",
                "an empress in phoenix crown, "
                "phoenix hairpin, "
                "imperial court",
                "a scholar in official hat, "
                "formal robe, "
                "court ceremony",
            ],
            "scene": [
                "imperial court, "
                "throne, "
                "attendants",
                "temple, "
                "incense, "
                "ceremony",
                "palace gate, "
                "guards, "
                "banners",
            ],
            "style": [
                "imperial Chinese portrait painting, "
                "mineral pigments, gold accents",
                "gongbi painting, "
                "precise details",
                "Ming and Qing dynasty court painting",
            ],
            "lighting": [
                "imperial radiance, golden",
                "candlelight, ceremony",
                "daylight, formal",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square album leaf",
                "horizontal handscroll",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "imperial Chinese portrait",
                "8k uhd, imperial grandeur",
            ],
        },
        "ornament": {
            "theme": "佩饰",
            "subject": [
                "a jade pendant, "
                "with silk cord, "
                "detail shot",
                "a jade bi and long tassel, "
                "with pearl, "
                "imperial",
                "hairpins, jade, gold, "
                "with pearl, "
                "detail"
            ],
            "scene": [
                "scholar's studio, "
                "jade, "
                "silk"
                ,
                "imperial court, "
                "jewelry box, "
                "silk"
                ,
                "garden, "
                "peonies, "
                "mirror"
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
                "Chinese jewelry painting",
                "8k uhd, refined elegance",
            ],
        },
    },

    # ============================================================
    # 戏曲
    # ============================================================
    "opera": {
        "beijing_opera": {
            "theme": "京剧",
            "subject": [
                "a Beijing opera performer, "
                "elaborate costume, "
                "painted face",
                "a Peking opera warrior, "
                "long pheasant feathers, "
                "dramatic pose",
                "a Beijing opera lady, "
                "with phoenix crown, "
                "flowing water sleeves",
            ],
            "scene": [
                "opera stage, "
                "drum, "
                "curtain",
                "palace scene, "
                "banner, "
                "throne",
                "mountain pass, "
                "warriors, "
                "flags"
            ],
            "style": [
                "traditional Chinese opera painting, "
                "gongbi details, vibrant colors",
                "in the style of Guan Liang",
                "modern Chinese opera poster",
            ],
            "lighting": [
                "stage light, dramatic",
                "lantern light, warm",
                "spotlight, theatrical",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square album leaf",
                "horizontal handscroll",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Beijing opera painting",
                "8k uhd, theatrical drama",
            ],
        },
        "kunqu": {
            "theme": "昆曲",
            "subject": [
                "a Kunqu opera performer, "
                "elegant costume, "
                "flowing water sleeves",
                "a Kunqu lady, "
                "with delicate makeup, "
                "in a garden scene",
                "Peony Pavilion scene, "
                "lovers, "
                "garden pavilion",
            ],
            "scene": [
                "garden pavilion, "
                "peonies, "
                "moon",
                "opera stage, "
                "silk curtain, "
                "lanterns",
                "scholar's garden, "
                "bamboo, "
                "lotus pond"
            ],
            "style": [
                "traditional Chinese opera painting, "
                "gongbi details, refined",
                "in the style of Gao马得",
                "Chinese gongbi figure painting",
            ],
            "lighting": [
                "soft stage light",
                "moonlight, silver",
                "lantern light, warm",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square album leaf",
                "horizontal handscroll",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Kunqu opera painting",
                "8k uhd, elegant refinement",
            ],
        },
        "sichuan_opera": {
            "theme": "川剧",
            "subject": [
                "Sichuan opera face-changing, "
                "multiple masks, "
                "dynamic pose",
                "a Sichuan opera warrior, "
                "with flag, "
                "dramatic gesture",
                "Sichuan opera lady, "
                "with long sleeves, "
                "elegant",
            ],
            "scene": [
                "Sichuan theater, "
                "lanterns, "
                "audience",
                "mountain pass, "
                "warriors, "
                "banners",
                "teahouse, "
                "stage, "
                "bamboo chairs",
            ],
            "style": [
                "traditional Sichuan opera painting, "
                "vibrant colors, precise details",
                "Chinese opera poster style",
                "gongbi figure painting",
            ],
            "lighting": [
                "stage light, dramatic",
                "lantern light, warm",
                "candlelight",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square album leaf",
                "horizontal handscroll",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Sichuan opera painting",
                "8k uhd, dramatic performance",
            ],
        },
        "yue_opera": {
            "theme": "越剧",
            "subject": [
                "a Yue opera performer, "
                "gentle appearance, "
                "elegant costume",
                "a Yue opera lady, "
                "with soft makeup, "
                "in a garden",
                "Liang Shanbo and Zhu Yingtai, "
                "butterflies, "
                "garden"
            ],
            "scene": [
                "garden, "
                "peonies, "
                "butterflies",
                "opera stage, "
                "silk curtain, "
                "lanterns",
                "willow trees, "
                "stream, "
                "stone bridge"
            ],
            "style": [
                "traditional Chinese opera painting, "
                "gongbi details, delicate",
                "in the style of Guan Liang",
                "Chinese opera poster style",
            ],
            "lighting": [
                "soft stage light",
                "moonlight, silver",
                "spring light, warm",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square album leaf",
                "horizontal handscroll",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Yue opera painting",
                "8k uhd, delicate romance",
            ],
        },
        "huangmei": {
            "theme": "黄梅戏",
            "subject": [
                "a Huangmei opera performer, "
                "rural style, "
                "elegant costume",
                "a Huangmei opera lady, "
                "with a fan, "
                "in a garden",
                "a Huangmei opera couple, "
                "in a mountain village",
            ],
            "scene": [
                "mountain village, "
                "rice fields, "
                "willow trees",
                "opera stage, "
                "bamboo curtain, "
                "lanterns",
                "tea garden, "
                "pavilion, "
                "distant peaks",
            ],
            "style": [
                "traditional Chinese opera painting, "
                "gongbi details, refined",
                "in the style of Gao马得",
                "Chinese folk painting style",
            ],
            "lighting": [
                "soft stage light",
                "daylight, warm",
                "sunset, warm",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square album leaf",
                "horizontal handscroll",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Huangmei opera painting",
                "8k uhd, pastoral warmth",
            ],
        },
        "opera_mask": {
            "theme": "脸谱",
            "subject": [
                "a Beijing opera mask, "
                "red face, black patterns, "
                "dramatic expression",
                "a set of opera masks, "
                "different colors and patterns",
                "a masked warrior, "
                "elaborate costume, "
                "dramatic pose"
            ],
            "scene": [
                "opera stage, "
                "drum, "
                "curtain",
                "mural background, "
                "opera motifs",
                "theater, "
                "lanterns, "
                "curtain"
            ],
            "style": [
                "traditional Chinese opera mask painting, "
                "vibrant colors, precise patterns",
                "in the style of modern Chinese opera poster",
                "gongbi details",
            ],
            "lighting": [
                "dramatic light",
                "stage light",
                "lantern light, warm",
            ],
            "composition": [
                "square album leaf",
                "vertical hanging scroll, lidu",
                "horizontal handscroll",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese opera mask painting",
                "8k uhd, dramatic color",
            ],
        },
    },

    # ============================================================
    # 佛道
    # ============================================================
    "buddhism": {
        "buddha": {
            "theme": "佛",
            "subject": [
                "a seated Buddha, "
                "lotus throne, "
                "mudra gesture, "
                "serene expression",
                "a Buddha triad, "
                "with attendants, "
                "lotus pond",
                "a reclining Buddha, "
                "parinirvana scene, "
                "disciples mourning"
            ],
            "scene": [
                "Buddhist temple, "
                "incense, "
                "lotus",
                "cave temple, "
                "murals, "
                "lamps",
                "paradise, "
                "jeweled trees, "
                "celestial music"
            ],
            "style": [
                "traditional Buddhist painting, "
                "mineral pigments, gold accents",
                "Dunhuang mural style",
                "in the style of Wu Daozi",
            ],
            "lighting": [
                "divine radiance, golden",
                "cave lamplight, warm",
                "celestial glow",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square mural",
                "horizontal handscroll",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "traditional Buddhist painting",
                "8k uhd, spiritual radiance",
            ],
        },
        "bodhisattva": {
            "theme": "菩萨",
            "subject": [
                "Guanyin Bodhisattva, "
                "holding a willow branch, "
                "flowing robes, "
                "compassionate gaze",
                "a Bodhisattva seated on a lotus, "
                "with attendants, "
                "halo of light",
                "a Bodhisattva with multiple arms, "
                "holding various implements, "
                "majestic"
            ],
            "scene": [
                "Buddhist paradise, "
                "jeweled trees, "
                "lotus ponds",
                "mountain retreat, "
                "waterfall, "
                "clouds",
                "cave temple, "
                "lamps, "
                "murals"
            ],
            "style": [
                "traditional Buddhist painting, "
                "mineral pigments, gold accents",
                "gongbi figure painting, "
                "flowing drapery lines",
                "Dunhuang mural style",
            ],
            "lighting": [
                "divine radiance, golden",
                "cave lamplight",
                "celestial glow",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square album leaf",
                "horizontal handscroll",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Bodhisattva painting",
                "8k uhd, compassionate grace",
            ],
        },
        "arhat": {
            "theme": "罗汉",
            "subject": [
                "an arhat with a staff, "
                "wrinkled face, "
                "wise expression",
                "a group of arhats, "
                "with various implements, "
                "in a cave",
                "an arhat with a tiger, "
                "taming the beast, "
                "mountain"
            ],
            "scene": [
                "mountain cave, "
                "stone, "
                "pine trees",
                "temple, "
                "incense, "
                "disciples",
                "forest, "
                "waterfall, "
                "tiger"
            ],
            "style": [
                "Chinese arhat painting, "
                "gongbi details, ink and wash",
                "in the style of Guanxiu",
                "Chan painting, xieyi"
            ],
            "lighting": [
                "cave light, mysterious",
                "daylight, natural",
                "moonlight, silver",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square album leaf",
                "horizontal handscroll",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "traditional Chinese arhat painting",
                "8k uhd, wise power",
            ],
        },
        "taoist": {
            "theme": "道教",
            "subject": [
                "Laozi riding an ox, "
                "flowing robes, "
                "long beard, "
                "wise expression",
                "a Taoist immortal, "
                "flying on a crane, "
                "auspicious clouds",
                "the Eight Immortals, "
                "celebrating, "
                "in the clouds"
            ],
            "scene": [
                "mountain pass, "
                "clouds, "
                "pine trees",
                "jade palace, "
                "peach trees, "
                "crane",
                "taoist temple, "
                "incense, "
                "ritual"
            ],
            "style": [
                "traditional Chinese Taoist painting, "
                "gongbi details, mineral pigments",
                "in the style of Wu Daozi",
                "folk painting style"
            ],
            "lighting": [
                "celestial radiance",
                "sunrise, golden",
                "cave light, mystical",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square album leaf",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "traditional Chinese Taoist painting",
                "8k uhd, transcendent spirit",
            ],
        },
        "immortal_land": {
            "theme": "仙境",
            "subject": [
                "a jade palace in clouds, "
                "cranes, "
                "peach trees, "
                "immortals",
                "an immortal island, "
                "with waterfall, "
                "jade terraces",
                "a landscape of immortals, "
                "flowing clouds, "
                "celestial music"
            ],
            "scene": [
                "cloud sea, "
                "distant peaks, "
                "cranes",
                "jade river, "
                "stone bridge, "
                "peach blossoms",
                "jade palace, "
                "clouds, "
                "sunrise"
            ],
            "style": [
                "traditional Chinese immortal painting, "
                "mineral pigments, gold accents",
                "blue-green landscape, "
                "decorative stylized",
                "in the style of Li Sixun"
            ],
            "lighting": [
                "celestial radiance, golden",
                "sunrise, warm",
                "moonlight, silver",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "horizontal handscroll",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese immortal land painting",
                "8k uhd, celestial beauty",
            ],
        },
        "chan": {
            "theme": "禅意",
            "subject": [
                "a Zen monk in meditation, "
                "on a rock, "
                "mountain stream, "
                "pine tree",
                "a Zen garden, "
                "raked gravel, "
                "stone, moss",
                "a lotus in a bowl, "
                "minimal composition, "
                "water drops"
            ],
            "scene": [
                "mountain stream, "
                "rocks, "
                "pine trees",
                "Zen garden, "
                "stone lantern, "
                "moss",
                "empty room, "
                "cushion, "
                "incense"
            ],
            "style": [
                "Chinese Chan painting, "
                "in the style of Liang Kai",
                "ink and wash, xieyi, "
                "minimal brushwork",
                "literati painting, vast negative space"
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
                "Chinese Zen painting",
                "8k uhd, zen simplicity",
            ],
        },
    },

    # ============================================================
    # 医药
    # ============================================================
    "medicine": {
        "herbal": {
            "theme": "本草",
            "subject": [
                "a collection of herbs, "
                "ginseng, goji, chrysanthemum, "
                "on a bamboo tray",
                "a scholar examining herbs, "
                "with magnifying glass, "
                "herbal pharmacopoeia",
                "herbs in a bowl, "
                "green leaves, roots, "
                "on xuan paper"
            ],
            "scene": [
                "scholar's studio, "
                "herbal medicine, "
                "books",
                "apothecary, "
                "herb drawers, "
                "balance scale",
                "garden, "
                "herbs, "
                "bamboo fence"
            ],
            "style": [
                "Chinese gongbi still life, "
                "precise botanical details",
                "Ming dynasty pharmacopoeia illustration",
                "literati painting, xieyi freehand"
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
                "Chinese herbal medicine painting",
                "8k uhd, botanical precision",
            ],
        },
        "acupuncture": {
            "theme": "针灸",
            "subject": [
                "a physician performing acupuncture, "
                "patient lying down, "
                "needles inserted",
                "acupuncture chart, "
                "meridians, "
                "anatomical details",
                "a bronze acupuncture statue, "
                "with meridians marked",
            ],
            "scene": [
                "clinic, "
                "herbal medicine, "
                "books",
                "scholar's studio, "
                "acupuncture chart, "
                "candles",
                "imperial court, "
                "physician, "
                "patient"
            ],
            "style": [
                "traditional Chinese medical painting, "
                "gongbi details, precise anatomy",
                "Ming dynasty medical illustration",
                "Qing dynasty painting",
            ],
            "lighting": [
                "soft interior light",
                "candlelight, warm",
                "daylight, natural",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "horizontal handscroll",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "traditional Chinese medicine painting",
                "8k uhd, medical precision",
            ],
        },
        "alchemy": {
            "theme": "炼丹",
            "subject": [
                "a Taoist alchemist, "
                "stirring a cauldron, "
                "cinnabar and mercury, "
                "smoke rising",
                "an alchemy furnace, "
                "with smoke, "
                "in a mountain cave",
                "a Taoist scholar, "
                "grinding medicine, "
                "in a studio",
            ],
            "scene": [
                "mountain cave, "
                "alchemy furnace, "
                "smoke",
                "scholar's studio, "
                "alchemy, "
                "books",
                "taoist temple, "
                "incense, "
                "cauldron"
            ],
            "style": [
                "Chinese Taoist painting, "
                "mineral pigments, gold accents",
                "gongbi details, precise",
                "in the style of Ming dynasty painting"
            ],
            "lighting": [
                "cave light, mysterious",
                "firelight, warm",
                "moonlight, silver",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square album leaf",
                "round fan",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese alchemy painting",
                "8k uhd, mystical atmosphere",
            ],
        },
        "medicine_king": {
            "theme": "药王",
            "subject": [
                "a medicine king, "
                "with herbal staff, "
                "long beard, "
                "wise expression",
                "Sun Simiao, "
                "with a tiger, "
                "mountain retreat",
                "a group of medicine kings, "
                "with various herbs, "
                "in a temple"
            ],
            "scene": [
                "mountain retreat, "
                "herbs, "
                "pine trees",
                "temple, "
                "incense, "
                "medicine statues",
                "garden, "
                "herbal medicine, "
                "bamboo"
            ],
            "style": [
                "Chinese folk painting, "
                "vibrant colors, gongbi details",
                "in the style of Ming dynasty painting",
                "traditional Chinese medicine painting"
            ],
            "lighting": [
                "daylight, warm",
                "morning light, fresh",
                "candlelight, temple",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square album leaf",
                "horizontal handscroll",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese medicine king painting",
                "8k uhd, wise compassion",
            ],
        },
        "physician": {
            "theme": "医者",
            "subject": [
                "a Chinese physician, "
                "pulse diagnosis, "
                "patient with wrist on cushion",
                "a physician examining herbs, "
                "with magnifying glass, "
                "herbal pharmacopoeia",
                "a physician writing a prescription, "
                "brush and ink, "
                "patient waiting"
            ],
            "scene": [
                "clinic, "
                "herbal medicine, "
                "books",
                "scholar's studio, "
                "patient, "
                "candles",
                "imperial court, "
                "physician, "
                "emperor"
            ],
            "style": [
                "Chinese gongbi painting, "
                "precise details, "
                "in the style of Ming dynasty illustration",
                "literati painting, xieyi freehand",
                "Ming dynasty medical illustration"
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
                "traditional Chinese physician painting",
                "8k uhd, wise compassion",
            ],
        },
        "herb_gathering": {
            "theme": "采药",
            "subject": [
                "a Taoist hermit gathering herbs, "
                "bamboo basket, "
                "on a mountain path",
                "a young boy gathering herbs, "
                "with a basket, "
                "in the forest",
                "an old man gathering lingzhi, "
                "on a cliff, "
                "with a rope"
            ],
            "scene": [
                "mountain path, "
                "mist, "
                "pine trees",
                "forest, "
                "stream, "
                "birds",
                "cliff, "
                "waterfall, "
                "clouds"
            ],
            "style": [
                "Chinese ink wash painting, "
                "minimal details",
                "literati painting, xieyi freehand",
                "Song dynasty landscape"
            ],
            "lighting": [
                "morning mist",
                "daylight, natural",
                "sunset, warm",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "horizontal handscroll",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "traditional Chinese herb gathering painting",
                "8k uhd, mountain serenity",
            ],
        },
    },

    # ============================================================
    # 民俗
    # ============================================================
    "folklore": {
        "paper_cutting": {
            "theme": "剪纸",
            "subject": [
                "Chinese paper cutting, "
                "red paper, "
                "window pattern, "
                "auspicious motifs",
                "paper cutting of a dragon, "
                "red paper, "
                "with intricate patterns",
                "paper cutting of children, "
                "with flowers, "
                "traditional New Year motif"
            ],
            "scene": [
                "window, red paper cutting, "
                "snow outside",
                "courtyard, red paper cutting, "
                "spring festival",
                "table, paper cutting, "
                "scissors, red paper"
            ],
            "style": [
                "Chinese paper cutting art, "
                "vibrant red, "
                "precise patterns",
                "traditional folk art, "
                "silhouette style",
                "New Year paper cutting"
            ],
            "lighting": [
                "backlight through window",
                "soft daylight",
                "firecracker light",
            ],
            "composition": [
                "square panel",
                "vertical hanging scroll, lidu",
                "round format",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese paper cutting",
                "8k uhd, intricate patterns",
            ],
        },
        "new_year_print": {
            "theme": "年画",
            "subject": [
                "a Chinese New Year print, "
                "door gods, "
                "vibrant colors, "
                "woodblock printing",
                "a New Year print of a chubby baby, "
                "with lotus, "
                "auspicious",
                "a New Year print of a kitchen god, "
                "with offerings, "
                "traditional"
            ],
            "scene": [
                "village, red lanterns, "
                "snow, warm windows",
                "imperial palace, "
                "banquet, firecrackers",
                "town street, "
                "red decorations, "
                "festive"
            ],
            "style": [
                "Chinese New Year print, "
                "woodblock printing, "
                "vibrant colors",
                "traditional folk art",
                "Ming and Qing dynasty print style"
            ],
            "lighting": [
                "lantern light, warm",
                "firecracker light",
                "snow reflection",
            ],
            "composition": [
                "square panel",
                "vertical hanging scroll, lidu",
                "horizontal handscroll",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese New Year print",
                "8k uhd, festive brightness",
            ],
        },
        "shadow_puppet": {
            "theme": "皮影",
            "subject": [
                "a Chinese shadow puppet, "
                "leather cutout, "
                "colorful dye, "
                "dramatic pose",
                "a shadow puppet warrior, "
                "with a sword, "
                "behind a backlit screen",
                "a shadow puppet lady, "
                "with flowing sleeves, "
                "elegant"
            ],
            "scene": [
                "shadow puppet theater, "
                "backlit screen, "
                "audience",
                "courtyard, "
                "backlit screen, "
                "night",
                "table, "
                "shadow puppets, "
                "leather, tools"
            ],
            "style": [
                "Chinese shadow puppet art, "
                "vibrant colors, "
                "silhouette style",
                "traditional folk art",
                "backlit silhouette style"
            ],
            "lighting": [
                "backlight, dramatic",
                "candlelight, warm",
                "stage light",
            ],
            "composition": [
                "horizontal panel",
                "square album leaf",
                "vertical hanging scroll, lidu",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese shadow puppet",
                "8k uhd, theatrical silhouette",
            ],
        },
        "puppet": {
            "theme": "木偶",
            "subject": [
                "a Chinese marionette puppet, "
                "with strings, "
                "elaborate costume",
                "a hand puppet, "
                "with vivid expression, "
                "dramatic pose",
                "a group of puppets, "
                "on a stage, "
                "colorful"
            ],
            "scene": [
                "puppet theater, "
                "stage, "
                "audience",
                "courtyard, "
                "stage, "
                "lanterns",
                "artisan workshop, "
                "puppets, "
                "wood, paints"
            ],
            "style": [
                "Chinese puppet art, "
                "vibrant colors, "
                "precise details",
                "traditional folk art",
                "gongbi details"
            ],
            "lighting": [
                "stage light",
                "candlelight, warm",
                "lantern light",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square album leaf",
                "horizontal handscroll",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese puppet painting",
                "8k uhd, theatrical charm",
            ],
        },
        "sugar_figure": {
            "theme": "糖人",
            "subject": [
                "a sugar figure artisan, "
                "blowing and shaping sugar, "
                "colorful sugar figures",
                "a sugar figure of a dragon, "
                "bright colors, "
                "on a stick",
                "sugar figures, "
                "on a stand, "
                "children watching"
            ],
            "scene": [
                "market street, "
                "sugar figure stand, "
                "crowd",
                "courtyard, "
                "sugar figures, "
                "children",
                "temple fair, "
                "sugar figures, "
                "lanterns"
            ],
            "style": [
                "Chinese folk art painting, "
                "vibrant colors, "
                "realistic details",
                "traditional folk painting",
                "gongbi details"
            ],
            "lighting": [
                "daylight, warm",
                "sunset, warm",
                "lantern light",
            ],
            "composition": [
                "horizontal handscroll",
                "square album leaf",
                "vertical hanging scroll, lidu",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese sugar figure painting",
                "8k uhd, sweet charm",
            ],
        },
        "yangko": {
            "theme": "秧歌",
            "subject": [
                "a Chinese yangko dance, "
                "colorful costumes, "
                "red ribbons, "
                "crowd celebrating",
                "children with drums, "
                "yangko dance, "
                "spring festival",
                "a yangko procession, "
                "flags, drums, "
                "festive"
            ],
            "scene": [
                "village street, "
                "yangko dance, "
                "snow",
                "imperial palace, "
                "yangko, "
                "firecrackers",
                "town square, "
                "yangko, "
                "festival"
            ],
            "style": [
                "Chinese folk painting, "
                "vibrant colors, "
                "precise details",
                "traditional folk painting",
                "gongbi details"
            ],
            "lighting": [
                "firecracker light, warm",
                "lantern light",
                "daylight, festive",
            ],
            "composition": [
                "horizontal handscroll",
                "square album leaf",
                "vertical hanging scroll, lidu",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Chinese yangko dance painting",
                "8k uhd, festive joy",
            ],
        },
    },

    # ============================================================
    # 朝代
    # ============================================================
    "dynasty": {
        "qin_han": {
            "theme": "秦汉",
            "subject": [
                "a Qin dynasty warrior, "
                "in armor, "
                "with a sword",
                "a Han dynasty lady, "
                "in flowing robe, "
                "with a mirror",
                "a Han dynasty scholar, "
                "writing on bamboo slips"
            ],
            "scene": [
                "great wall, "
                "mountain pass, "
                "banners",
                "imperial palace, "
                "silken curtains, "
                "lanterns",
                "bamboo grove, "
                "scholar's studio, "
                "bamboo slips"
            ],
            "style": [
                "Qin and Han dynasty painting, "
                "mineral pigments, precise details",
                "gongbi figure painting",
                "in the style of Han dynasty fresco"
            ],
            "lighting": [
                "daylight, warm",
                "candlelight, warm",
                "moonlight, silver",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Qin and Han dynasty painting",
                "8k uhd, ancient grandeur",
            ],
        },
        "wei_jin": {
            "theme": "魏晋",
            "subject": [
                "a Wei-Jin scholar, "
                "loose robe, "
                "with wine cup, "
                "drunken revelry",
                "a Seven Sages of the Bamboo Grove figure, "
                "playing the guqin",
                "a lady in Wei-Jin dress, "
                "with flowing robes, "
                "elegant"
            ],
            "scene": [
                "bamboo grove, "
                "stream, "
                "rocks",
                "mountain pavilion, "
                "clouds, "
                "pine",
                "scholar's garden, "
                "moon, "
                "wine"
            ],
            "style": [
                "Wei-Jin dynasty painting, "
                "gongbi details, refined",
                "in the style of Gu Kaizhi",
                "literati painting, xieyi freehand"
            ],
            "lighting": [
                "soft morning light",
                "moonlight, silver",
                "afternoon, warm",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Wei-Jin dynasty painting",
                "8k uhd, philosophical elegance",
            ],
        },
        "sui_tang": {
            "theme": "隋唐",
            "subject": [
                "a Tang dynasty lady, "
                "plump and elegant, "
                "high-waisted silk robe, "
                "elaborate hairpins",
                "a Tang dynasty official, "
                "in court dress, "
                "with tablet",
                "a Tang dynasty warrior, "
                "in armor, "
                "on a horse"
            ],
            "scene": [
                "imperial court, "
                "banquet, "
                "lanterns",
                "palace garden, "
                "peonies, "
                "lotus pond",
                "street market, "
                "foreign merchants, "
                "bright colors"
            ],
            "style": [
                "Tang dynasty court painting, "
                "in the style of Zhou Fang and Zhang Xuan",
                "gongbi beauty painting, "
                "fine-line drawing, color washes",
                "Tang dynasty mural style"
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
                "Tang dynasty court painting",
                "8k uhd, imperial splendor",
            ],
        },
        "song_yuan": {
            "theme": "宋元",
            "subject": [
                "a Song dynasty scholar, "
                "in simple robe, "
                "contemplative",
                "a Song dynasty lady, "
                "in elegant dress, "
                "with a fan",
                "a Yuan dynasty warrior, "
                "on horseback, "
                "with a bow"
            ],
            "scene": [
                "scholar's studio, "
                "bamboo, "
                "books",
                "mountain stream, "
                "pavilion, "
                "mist",
                "steppe, "
                "grassland, "
                "horses"
            ],
            "style": [
                "Song dynasty painting, "
                "gongbi details, refined",
                "in the style of Li Gonglin and Zhao Mengfu",
                "literati painting, xieyi freehand"
            ],
            "lighting": [
                "soft morning light",
                "moonlight, silver",
                "autumn light, warm",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Song and Yuan dynasty painting",
                "8k uhd, refined literati",
            ],
        },
        "ming_qing": {
            "theme": "明清",
            "subject": [
                "a Ming dynasty lady, "
                "in elegant dress, "
                "with a fan",
                "a Qing dynasty official, "
                "in formal robe, "
                "with mandarin square",
                "a Ming dynasty scholar, "
                "writing calligraphy"
            ],
            "scene": [
                "imperial garden, "
                "peonies, "
                "rockery",
                "scholar's studio, "
                "books, "
                "ink stone",
                "tea room, "
                "bamboo, "
                "stone lantern"
            ],
            "style": [
                "Ming and Qing dynasty painting, "
                "gongbi details, refined",
                "in the style of Tang Yin and Wen Zhengming",
                "literati painting, xieyi freehand"
            ],
            "lighting": [
                "soft interior light",
                "candlelight, warm",
                "spring light, warm",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square album leaf",
                "horizontal handscroll",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Ming and Qing dynasty painting",
                "8k uhd, refined elegance",
            ],
        },
        "republican": {
            "theme": "民国",
            "subject": [
                "a Republican era lady, "
                "qipao, "
                "waving fan, "
                "shanghai style",
                "a Republican era scholar, "
                "in long gown, "
                "with book",
                "a Republican era soldier, "
                "in uniform, "
                "with rifle"
            ],
            "scene": [
                "Shanghai street, "
                "tram, "
                "neon signs",
                "scholar's studio, "
                "books, "
                "ink stone",
                "mountain village, "
                "war, "
                "smoke"
            ],
            "style": [
                "Republican era painting, "
                "in the style of Shanghai school",
                "modern Chinese painting, "
                "gongbi details",
                "old Shanghai poster style"
            ],
            "lighting": [
                "soft interior light",
                "electric light, warm",
                "twilight, romantic",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "square album leaf",
                "horizontal handscroll",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Republican era Chinese painting",
                "8k uhd, elegant modernity",
            ],
        },
    },

    # ============================================================
    # 地域
    # ============================================================
    "region": {
        "jiangnan": {
            "theme": "江南",
            "subject": [
                "a Jiangnan water town, "
                "stone bridge, "
                "willow trees, "
                "small boats",
                "a Jiangnan garden, "
                "pavilion, "
                "lotus pond",
                "a Jiangnan lady, "
                "with umbrella, "
                "rain"
            ],
            "scene": [
                "water town, "
                "canal, "
                "stone bridge",
                "misty lake, "
                "lotus, "
                "willow trees",
                "garden, "
                "rockery, "
                "bamboo"
            ],
            "style": [
                "Chinese ink wash painting, "
                "minimal details",
                "literati painting, xieyi freehand",
                "in the style of Wen Zhengming"
            ],
            "lighting": [
                "misty morning",
                "rainy day, soft",
                "moonlight, silver",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Jiangnan water town painting",
                "8k uhd, elegant atmosphere",
            ],
        },
        "saibei": {
            "theme": "塞北",
            "subject": [
                "a northern grassland, "
                "horses, "
                "banner, "
                "distant mountains",
                "a nomad horseman, "
                "with bow, "
                "winter steppe",
                "a snowy mountain pass, "
                "warriors, "
                "dramatic sky"
            ],
            "scene": [
                "grassland, "
                "horses, "
                "banners",
                "mountain pass, "
                "snow, "
                "warriors",
                "desert, "
                "sand dunes, "
                "camels"
            ],
            "style": [
                "Chinese ink wash painting, "
                "dramatic brushwork",
                "in the style of Zhao Mengfu",
                "literati painting, xieyi freehand"
            ],
            "lighting": [
                "dramatic light",
                "sunset, warm",
                "storm light",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Northern China painting",
                "8k uhd, heroic atmosphere",
            ],
        },
        "xiyu": {
            "theme": "西域",
            "subject": [
                "a silk road caravan, "
                "camels, merchants, "
                "distant dunes",
                "a Buddhist cave temple, "
                "with murals, "
                "lamps",
                "a Persian dancer, "
                "with flowing robes, "
                "music"
            ],
            "scene": [
                "desert, "
                "sand dunes, "
                "distant oasis",
                "Buddhist cave, "
                "murals, "
                "lamps",
                "market, "
                "merchants, "
                "fabrics"
            ],
            "style": [
                "Dunhuang mural style, "
                "mineral pigments, gold accents",
                "Tang dynasty painting, "
                "in the style of Zhang Qian",
                "silk road painting"
            ],
            "lighting": [
                "sunset, golden",
                "cave lamplight, warm",
                "desert light, warm",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square mural",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Silk Road painting",
                "8k uhd, exotic elegance",
            ],
        },
        "lingnan": {
            "theme": "岭南",
            "subject": [
                "a Lingnan garden, "
                "banyan trees, "
                "lotus pond, "
                "pavilion",
                "a Cantonese lady, "
                "with a fan, "
                "in a garden",
                "a Lingnan scholar, "
                "in a bamboo grove"
            ],
            "scene": [
                "banyan grove, "
                "river, "
                "boats",
                "garden, "
                "rockery, "
                "lotus pond",
                "tea house, "
                "bamboo furniture, "
                "dim sum"
            ],
            "style": [
                "Chinese ink wash painting, "
                "in the style of Gao Jianfu",
                "lingnan school painting",
                "gongbi details, tropical colors"
            ],
            "lighting": [
                "summer sunlight, warm",
                "afternoon, dappled",
                "sunset, tropical",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Lingnan school painting",
                "8k uhd, tropical elegance",
            ],
        },
        "bashu": {
            "theme": "巴蜀",
            "subject": [
                "a Bashu mountain landscape, "
                "steep cliffs, "
                "river, "
                "distant temples",
                "a Sichuan teahouse, "
                "bamboo chairs, "
                "tea sets",
                "a Ba lady, "
                "with a fan, "
                "in a mountain garden"
            ],
            "scene": [
                "mountain valley, "
                "mist, "
                "temples",
                "teahouse, "
                "bamboo, "
                "tea",
                "river, "
                "boat, "
                "mountains"
            ],
            "style": [
                "Chinese ink wash painting, "
                "in the style of Zhang Daqian",
                "Sichuan school painting",
                "literati painting, xieyi freehand"
            ],
            "lighting": [
                "misty morning",
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
                "Sichuan painting",
                "8k uhd, misty elegance",
            ],
        },
        "zhongyuan": {
            "theme": "中原",
            "subject": [
                "a Central Plains landscape, "
                "Yellow River, "
                "ancient pines, "
                "distant mountains",
                "a Central Plains scholar, "
                "reading under a tree",
                "a Zhongyuan lady, "
                "in traditional dress"
            ],
            "scene": [
                "Yellow River, "
                "mountains, "
                "pines",
                "scholar's studio, "
                "ancient books, "
                "ink stone",
                "ancient city, "
                "walls, "
                "temples"
            ],
            "style": [
                "Chinese ink wash painting, "
                "in the style of Fan Kuan",
                "Song dynasty monumental landscape",
                "literati painting, xieyi freehand"
            ],
            "lighting": [
                "morning light, warm",
                "afternoon, natural",
                "sunset, golden",
            ],
            "composition": [
                "vertical hanging scroll, lidu",
                "horizontal handscroll",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "Central Plains painting",
                "8k uhd, ancient grandeur",
            ],
        },
    },

    # ============================================================
    # 现代融合
    # ============================================================
    "modern": {
        "guochao": {
            "theme": "国潮",
            "subject": [
                "a modern Chinese lady in guochao outfit, "
                "traditional patterns on modern cut",
                "a guochao sneaker, "
                "with dragon motifs, "
                "neon accents",
                "a guochao poster, "
                "with bold colors, "
                "Chinese motifs"
            ],
            "scene": [
                "modern city, "
                "neon lights, "
                "Chinese architecture",
                "art gallery, "
                "guochao poster, "
                "modern",
                "street style, "
                "bamboo, "
                "concrete"
            ],
            "style": [
                "modern Chinese illustration, "
                "bold graphic design",
                "guochao aesthetic, "
                "flat colors, traditional patterns",
                "pop art meets traditional Chinese"
            ],
            "lighting": [
                "neon light, colorful",
                "studio light, bright",
                "sunset, modern",
            ],
            "composition": [
                "poster format",
                "square album leaf",
                "horizontal panel",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "guochao poster",
                "8k uhd, bold design",
            ],
        },
        "new_chinese": {
            "theme": "新中式",
            "subject": [
                "a modern Chinese interior, "
                "with Ming-style furniture, "
                "minimalist",
                "a lady in a modern qipao, "
                "with lotus pattern, "
                "minimal",
                "a modern Chinese garden, "
                "with abstract stones, "
                "water features"
            ],
            "scene": [
                "modern interior, "
                "Ming furniture, "
                "minimalist",
                "tea room, "
                "bamboo, "
                "stone",
                "modern garden, "
                "abstract, "
                "minimal"
            ],
            "style": [
                "modern Chinese illustration, "
                "minimalist, "
                "traditional motifs",
                "new Chinese aesthetic, "
                "clean lines",
                "in the style of contemporary Chinese design"
            ],
            "lighting": [
                "soft interior light",
                "natural light",
                "minimalist studio light",
            ],
            "composition": [
                "horizontal panel",
                "square album leaf",
                "vertical hanging scroll, lidu",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "new Chinese design",
                "8k uhd, minimalist elegance",
            ],
        },
        "cyber_chinese": {
            "theme": "赛博国风",
            "subject": [
                "a cyberpunk Chinese city, "
                "neon signs with Chinese characters, "
                "traditional pagodas with neon lights",
                "a cyber samurai, "
                "with traditional armor "
                "and modern weapons",
                "a cyberpunk Chinese lady, "
                "with holographic patterns"
            ],
            "scene": [
                "neon city, "
                "rain, "
                "Chinese architecture",
                "underground club, "
                "neon lights, "
                "Chinese motifs",
                "cyber temple, "
                "holograms, "
                "incense"
            ],
            "style": [
                "cyberpunk Chinese illustration, "
                "neon colors, "
                "traditional motifs",
                "cyberpunk meets traditional Chinese",
                "in the style of Blade Runner meets China"
            ],
            "lighting": [
                "neon light, colorful",
                "rain reflection",
                "holographic glow",
            ],
            "composition": [
                "poster format",
                "horizontal panel",
                "vertical hanging scroll, lidu",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "cyberpunk Chinese illustration",
                "8k uhd, futuristic elegance",
            ],
        },
        "ink_tech": {
            "theme": "水墨科技",
            "subject": [
                "a mountain landscape, "
                "rendered in ink wash, "
                "with circuit board patterns",
                "a bird, "
                "in ink wash style, "
                "with glowing lines",
                "a Chinese scholar, "
                "with holographic tablet"
            ],
            "scene": [
                "mountain valley, "
                "ink wash, "
                "glowing lines",
                "scholar's studio, "
                "ink stone, "
                "holographic"
                ,
                "cyber garden, "
                "ink wash, "
                "circuit patterns"
            ],
            "style": [
                "ink wash meets tech, "
                "traditional brushwork "
                "with glowing lines",
                "in the style of contemporary Chinese artist",
                "traditional meets futuristic"
            ],
            "lighting": [
                "soft ink light, "
                "glowing lines",
                "blue hour, tech",
            ],
            "composition": [
                "horizontal handscroll",
                "vertical hanging scroll, lidu",
                "square album leaf",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "ink tech illustration",
                "8k uhd, futuristic elegance",
            ],
        },
        "future_tang": {
            "theme": "未来唐",
            "subject": [
                "a future Tang dynasty lady, "
                "with modern tech accessories, "
                "high-waisted robe",
                "a future Tang dynasty city, "
                "with floating pagodas, "
                "neon lights",
                "a future Tang dynasty warrior, "
                "in armor with glowing accents"
            ],
            "scene": [
                "future city, "
                "pagodas, "
                "neon lights",
                "space station, "
                "Tang motifs, "
                "holograms",
                "imperial palace, "
                "holographic banners"
            ],
            "style": [
                "futuristic Tang dynasty illustration, "
                "traditional motifs, "
                "glowing accents",
                "sci-fi meets Tang dynasty",
                "in the style of cyberpunk meets Chinese"
            ],
            "lighting": [
                "neon light, colorful",
                "holographic glow",
                "sci-fi light",
            ],
            "composition": [
                "poster format",
                "horizontal panel",
                "vertical hanging scroll, lidu",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "futuristic Tang dynasty illustration",
                "8k uhd, sci-fi elegance",
            ],
        },
        "mecha_classic": {
            "theme": "机械古典",
            "subject": [
                "a mecha warrior in traditional armor design, "
                "with mechanical joints, "
                "glowing accents",
                "a mecha dragon, "
                "with traditional dragon design, "
                "metal scales",
                "a mecha pagoda, "
                "with rotating levels, "
                "glowing lights"
            ],
            "scene": [
                "future city, "
                "mecha, "
                "neon",
                "battlefield, "
                "mecha, "
                "smoke",
                "temple, "
                "mecha guardian, "
                "incense"
            ],
            "style": [
                "mecha illustration, "
                "traditional Chinese design, "
                "metal details",
                "sci-fi meets traditional Chinese",
                "in the style of Japanese mecha meets Chinese"
            ],
            "lighting": [
                "neon light, dramatic",
                "metal reflection",
                "sunset, silhouette",
            ],
            "composition": [
                "poster format",
                "horizontal panel",
                "vertical hanging scroll, lidu",
            ],
            "quality": [
                "masterpiece, best quality, highly detailed, "
                "mecha Chinese illustration",
                "8k uhd, mechanical elegance",
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