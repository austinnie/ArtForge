# config/art_config.py
"""
ArtForge 艺术风格配置

包含：
  - 艺术分类枚举
  - 画幅枚举
  - 日式画风
  - 妖怪图鉴
  - 古风画风
  - 源氏物语场景
  - 唐风画风
  - 题词印章配置
  - 做旧处理配置
"""

from enum import Enum


# ============================================================
# 枚举
# ============================================================

class ArtCategory(Enum):
    """艺术分类"""
    JAPANESE = ("japanese", "日本文化")
    YOKAI = ("yokai", "妖怪")
    GUFENG = ("gufeng", "古风")
    GENJI = ("genji", "源氏物语")
    TANG = ("tang", "唐风")
    ART_NUDE = ("art_nude", "艺术裸体")  # 敏感，先留骨架

    def __init__(self, key, cn):
        self.key = key
        self.cn = cn


class ScrollType(Enum):
    """画幅类型"""
    LIZHOU = ("立轴", "9:16", "vertical hanging scroll")
    HENGJUAN = ("横卷", "16:9", "horizontal handscroll")
    PINGFENG = ("屏风", "4:3", "folding screen")
    TUANSHAN = ("团扇", "1:1", "round fan")
    CEYE = ("册页", "3:4", "album leaf")

    def __init__(self, cn, ratio, en):
        self.cn = cn
        self.ratio = ratio
        self.en = en

    @classmethod
    def get_by_cn(cls, cn):
        for s in cls:
            if s.cn == cn:
                return s
        return cls.LIZHOU


# ============================================================
# 日式画风
# ============================================================

JAPANESE_STYLES = {
    "ukiyo_e": {
        "name": "浮世绘",
        "prompt": (
            "ukiyo-e woodblock print, flat colors, bold outlines, "
            "Edo period style, Hokusai and Hiroshige influence, "
            "visible woodblock grain, traditional Japanese print"
        ),
        "palette": ["靛蓝", "朱红", "土黄", "墨黑", "松绿"],
        "keywords": ["浮世绘", "版画", "江户", "ukiyo-e", "woodblock"],
    },
    "nihonga": {
        "name": "日本画",
        "prompt": (
            "nihonga, traditional Japanese painting, mineral pigments, "
            "gold leaf, delicate brushwork, Taisho and Showa era, "
            "silk or paper support, refined elegance"
        ),
        "palette": ["金箔", "岩绿", "朱砂", "群青", "胡粉"],
        "keywords": ["日本画", "岩彩", "金箔", "nihonga"],
    },
    "sumi_e": {
        "name": "水墨",
        "prompt": (
            "sumi-e ink wash painting, minimal, negative space, "
            "zen aesthetic, Sesshu and Hasegawa Tohaku style, "
            "monochrome ink on paper, spontaneous brushwork"
        ),
        "palette": ["墨黑", "留白", "淡灰", "焦墨"],
        "keywords": ["水墨", "墨绘", "禅意", "sumi-e"],
    },
    "byobu_e": {
        "name": "屏风绘",
        "prompt": (
            "byobu-e folding screen painting, gold leaf background, "
            "Kano school, Rimpa school, decorative, "
            "seasonal motifs, multi-panel composition"
        ),
        "palette": ["金", "翠绿", "朱", "蓝", "银"],
        "keywords": ["屏风", "金屏风", "狩野派", "琳派"],
    },
    "emaki": {
        "name": "绘卷物",
        "prompt": (
            "emaki picture scroll, yamato-e style, continuous narrative, "
            "architectural details, Heian or Kamakura period, "
            "handscroll format, tsukuri-e painting"
        ),
        "palette": ["朱", "群青", "绿青", "墨"],
        "keywords": ["绘卷", "大和绘", "源氏物语绘卷"],
    },
}


# ============================================================
# 妖怪图鉴
# ============================================================

YOKAI_DICT = {
    "tengu": {
        "name": "天狗",
        "prompt": (
            "tengu, red face, long nose, feathered wings, "
            "mountain hermit, yamabushi attire, fierce expression, "
            "hauchiwa fan, crow tengu or long-nose tengu"
        ),
        "scene": "deep mountain forest, misty peaks, ancient cedars",
        "keywords": ["天狗", "tengu", "山伏", "鞍马山"],
    },
    "kappa": {
        "name": "河童",
        "prompt": (
            "kappa, green reptilian humanoid, water dish on head, "
            "webbed hands, turtle shell, beak, river creature, "
            "mischievous expression, cucumber"
        ),
        "scene": "riverbank, clear stream, lotus leaves, summer",
        "keywords": ["河童", "kappa", "河童渊", "黄瓜"],
    },
    "kitsune": {
        "name": "九尾狐",
        "prompt": (
            "kitsune, nine-tailed fox spirit, white fur, "
            "golden eyes, elegant, Inari shrine, "
            "flowing tails, mystical aura, beautiful woman or fox"
        ),
        "scene": "Inari shrine, torii gates, red lanterns, autumn",
        "keywords": ["九尾狐", "kitsune", "稻荷神", "狐火"],
    },
    "yuki_onna": {
        "name": "雪女",
        "prompt": (
            "yuki-onna, snow woman, pale white skin, long black hair, "
            "blue lips, white kimono, ethereal, "
            "snowy mountain, freezing mist, tragic beauty"
        ),
        "scene": "snowy mountain pass, blizzard, frozen pine trees",
        "keywords": ["雪女", "yuki-onna", "雪女传说"],
    },
    "oni": {
        "name": "鬼",
        "prompt": (
            "oni demon, horned ogre, red or blue skin, "
            "tiger skin loincloth, kanabo club, fierce, "
            "sharp teeth, wild hair, muscular"
        ),
        "scene": "hellish landscape, volcanic rocks, red sky, flames",
        "keywords": ["鬼", "oni", "赤鬼", "青鬼"],
    },
    "kitsune_bi": {
        "name": "狐火",
        "prompt": (
            "kitsune-bi fox fire, blue flames, ghostly, "
            "forest at night, mysterious, floating lights, "
            "procession of foxes, wedding procession"
        ),
        "scene": "dark forest at night, blue flames, misty",
        "keywords": ["狐火", "kitsune-bi", "狐狸嫁女"],
    },
    "hyakki_yagyo": {
        "name": "百鬼夜行",
        "prompt": (
            "hyakki yagyo night parade of one hundred demons, "
            "procession of yokai, lanterns, chaos, "
            "Toriyama Sekien style, ukiyo-e, many creatures"
        ),
        "scene": "night street, paper lanterns, full moon, mist",
        "keywords": ["百鬼夜行", "hyakki yagyo", "鸟山石燕"],
    },
    "kitsune_no_yomeiri": {
        "name": "狐狸嫁女",
        "prompt": (
            "kitsune no yomeiri, fox wedding procession, "
            "fox spirits in human form, lanterns, "
            "rainy sunny day, mysterious, elegant"
        ),
        "scene": "forest path in light rain, sunbeams, lanterns",
        "keywords": ["狐狸嫁女", "狐の嫁入り"],
    },
    "noppera_bo": {
        "name": "野篦坊",
        "prompt": (
            "noppera-bo, faceless ghost, smooth blank face, "
            "woman in kimono, unsettling, "
            "traditional Japanese horror, eerie"
        ),
        "scene": "dark alley at night, paper lantern, mist",
        "keywords": ["野篦坊", "noppera-bo", "无脸怪"],
    },
    "roku_ro_kubi": {
        "name": "辘轳首",
        "prompt": (
            "rokurokubi, long-necked woman, "
            "stretching neck at night, kimono, "
            "traditional Japanese yokai, eerie beauty"
        ),
        "scene": "Edo period bedroom, paper screens, candlelight",
        "keywords": ["辘轳首", "rokurokubi", "长颈妖怪"],
    },
}


# ============================================================
# 古风画风
# ============================================================

GUFENG_STYLES = {
    "shui_mo": {
        "name": "水墨",
        "prompt": (
            "Chinese ink wash painting, shui-mo, monochrome, "
            "literati painting, xieyi style, "
            "rice paper, calligraphic brushwork"
        ),
        "palette": ["墨", "留白", "淡赭"],
        "keywords": ["水墨", "写意", "文人画"],
    },
    "gong_bi": {
        "name": "工笔",
        "prompt": (
            "Chinese gongbi painting, meticulous brushwork, "
            "fine lines, layered colors, "
            "silk or rice paper, court painting style"
        ),
        "palette": ["朱砂", "石青", "石绿", "藤黄", "蛤粉"],
        "keywords": ["工笔", "重彩", "院体画"],
    },
    "qing_lv": {
        "name": "青绿山水",
        "prompt": (
            "Chinese blue-and-green landscape, qing-lv shanshui, "
            "mineral pigments, gold outline, "
            "Tang and Song dynasty style, panoramic"
        ),
        "palette": ["石青", "石绿", "泥金", "赭石"],
        "keywords": ["青绿山水", "金碧山水"],
    },
    "jian_bi": {
        "name": "减笔",
        "prompt": (
            "Chinese abbreviated brush style, jian-bi, "
            "minimal strokes, Liang Kai style, "
            "zen painting, spontaneous"
        ),
        "palette": ["墨", "淡彩"],
        "keywords": ["减笔", "梁楷", "禅画"],
    },
    "bai_miao": {
        "name": "白描",
        "prompt": (
            "Chinese baimiao line drawing, pure outline, "
            "no color, fine ink lines, "
            "Li Gonglin style, elegant"
        ),
        "palette": ["墨线", "留白"],
        "keywords": ["白描", "线描", "李公麟"],
    },
}


# ============================================================
# 源氏物语场景
# ============================================================

GENJI_SCENES = {
    "heian_court": {
        "name": "平安宫廷",
        "prompt": (
            "Heian period imperial court, shinden-zukuri architecture, "
            "veranda, garden with pond, "
            "courtiers in sokutai, ladies in junihitoe"
        ),
        "keywords": ["平安", "宫廷", "寝殿造"],
    },
    "junihitoe": {
        "name": "十二单",
        "prompt": (
            "Heian lady in junihitoe, twelve-layer kimono, "
            "long black hair, fan, "
            "seated on veranda, poetic expression"
        ),
        "keywords": ["十二单", "女房装束"],
    },
    "byobu_emaki": {
        "name": "屏风绘卷",
        "prompt": (
            "Genji monogatari emaki style, "
            "illustrated handscroll, yamato-e, "
            "court scenes, sliding doors, gold clouds"
        ),
        "keywords": ["源氏物语绘卷", "大和绘"],
    },
    "moon_viewing": {
        "name": "观月",
        "prompt": (
            "Heian court moon viewing party, "
            "autumn night, full moon, "
            "courtiers playing koto and flute, poetry"
        ),
        "keywords": ["观月", "月见", "中秋"],
    },
    "cherry_blossom": {
        "name": "赏樱",
        "prompt": (
            "Heian court cherry blossom viewing, "
            "spring, petals falling, "
            "ladies in junihitoe, courtiers, poetry"
        ),
        "keywords": ["赏樱", "花见", "春"],
    },
}


# ============================================================
# 唐风画风
# ============================================================

TANG_STYLES = {
    "dunhuang": {
        "name": "敦煌壁画",
        "prompt": (
            "Dunhuang mural style, mineral pigments, "
            "flying apsaras, Tang dynasty Buddhist art, "
            "weathered fresco, cave temple, "
            "feitian, celestial dancers"
        ),
        "palette": ["土红", "石青", "石绿", "赭石", "黑"],
        "keywords": ["敦煌", "飞天", "壁画"],
    },
    "tang_beauty": {
        "name": "唐仕女",
        "prompt": (
            "Tang dynasty court lady, plump figure, "
            "high bun, colorful silk dress, "
            "Zhou Fang style, elegant, "
            "floral hairpin, round face"
        ),
        "palette": ["朱红", "鹅黄", "翠绿", "金"],
        "keywords": ["唐仕女", "簪花仕女图", "周昉"],
    },
    "tang_palace": {
        "name": "大唐宫苑",
        "prompt": (
            "Tang dynasty palace scene, "
            "grand architecture, "
            "court ladies playing music, "
            "silk robes, gold ornaments"
        ),
        "keywords": ["大唐", "宫苑", "仕女"],
    },
    "tang_horse": {
        "name": "唐马",
        "prompt": (
            "Tang dynasty horse, "
            "ceramic figurine style, "
            "muscular, saddle, "
            "Han Gan painting influence"
        ),
        "keywords": ["唐马", "韩干", "昭陵六骏"],
    },
}


# ============================================================
# 艺术裸体（敏感，先留骨架）
# ============================================================

ART_NUDE_STYLES = {
    # ⚠️ 敏感内容，暂留骨架
    # 未来填充时需：
    #   1. 保持艺术性（浮世绘春画、能剧面具、花魁等传统美学）
    #   2. 在 core/safety.py 加艺术豁免规则
    #   3. 避免现代色情元素
    #
    # 预留 key：
    #   - shunga: 春画（浮世绘风格）
    #   - onsen: 温泉汤女
    #   - oiran: 花魁
    #   - noh_mask: 能剧面具下的身体
    #   - yuujo: 游女
    #   - geisha_back: 艺伎背影
    "_placeholder": {
        "name": "（待填充）",
        "prompt": "",
        "keywords": [],
    },
}


# ============================================================
# 画幅尺寸
# ============================================================

SCROLL_SIZES = {
    "立轴": {"ratio": "9:16", "width": 768, "height": 1365},
    "横卷": {"ratio": "16:9", "width": 1365, "height": 768},
    "屏风": {"ratio": "4:3", "width": 1024, "height": 768},
    "团扇": {"ratio": "1:1", "width": 1024, "height": 1024},
    "册页": {"ratio": "3:4", "width": 768, "height": 1024},
}


# ============================================================
# 题词印章配置
# ============================================================

INSCRIPTION_CONFIG = {
    "formats": {
        "hanshi": "汉诗（五言/七言）",
        "waka": "和歌（5-7-5-7-7）",
        "haiku": "俳句（5-7-5）",
        "tiba": "题跋（散文）",
        "kuanshi": "款识（作者署名）",
    },
    "default_format": "waka",
    "seal_types": {
        "zhu_wen": {
            "name": "朱文印",
            "desc": "阳刻，红字白底",
            "color": "#C1272D",
        },
        "bai_wen": {
            "name": "白文印",
            "desc": "阴刻，白字红底",
            "color": "#C1272D",
        },
    },
    "seal_positions": {
        "右下": (0.85, 0.92),
        "左下": (0.10, 0.92),
        "右上": (0.85, 0.05),
        "左上": (0.10, 0.05),
    },
    "seal_default_position": "左下",
    "font_family": "毛笔楷书",
}


# ============================================================
# 做旧处理
# ============================================================

AGING_CONFIG = {
    "paper_textures": {
        "xuan_paper": {
            "name": "宣纸",
            "color": "#F5EFE0",
            "noise": 0.03,
        },
        "silk": {
            "name": "绢本",
            "color": "#E8DCC0",
            "noise": 0.02,
        },
        "aged_paper": {
            "name": "老纸",
            "color": "#D9C9A3",
            "noise": 0.05,
        },
        "brown_paper": {
            "name": "褐纸",
            "color": "#C4A575",
            "noise": 0.06,
        },
    },
    "effects": {
        "foxing": {
            "name": "霉斑",
            "desc": "随机褐色斑点",
            "density": 0.001,
        },
        "yellowing": {
            "name": "泛黄",
            "desc": "整体色调偏移",
            "strength": 0.15,
        },
        "creasing": {
            "name": "折痕",
            "desc": "随机折痕线",
            "count": 3,
        },
        "edge_wear": {
            "name": "边缘磨损",
            "desc": "四周暗角",
            "strength": 0.3,
        },
        "ink_bleed": {
            "name": "墨韵晕染",
            "desc": "墨色扩散",
            "strength": 0.2,
        },
    },
    "default_texture": "xuan_paper",
    "default_effects": ["yellowing", "edge_wear"],
}


# ============================================================
# 主色板（供各画风共享）
# ============================================================

MASTER_PALETTE = {
    "传统颜料": {
        "朱砂": "#C1272D",
        "朱膘": "#E34234",
        "石青": "#1D4E89",
        "石绿": "#3C8C6A",
        "藤黄": "#F4C430",
        "赭石": "#8B4513",
        "蛤粉": "#F5F5DC",
        "泥金": "#D4AF37",
        "墨": "#1C1C1C",
        "留白": "#FFFFFF",
    },
    "日本传统色": {
        "茜色": "#B7282E",
        "朱色": "#EB6238",
        "山吹色": "#F8B500",
        "若草色": "#C3D825",
        "青竹色": "#7EBEAB",
        "群青色": "#4C6CB3",
        "藤色": "#8B81C3",
        "桜色": "#FEF4F4",
        "墨色": "#1C1C1C",
        "金茶": "#C79E3B",
    },
}


# ============================================================
# 工具函数
# ============================================================

def get_style_prompt(category: str, style_key: str) -> str:
    """根据分类和 key 获取画风 prompt"""
    mapping = {
        "japanese": JAPANESE_STYLES,
        "gufeng": GUFENG_STYLES,
        "tang": TANG_STYLES,
        "art_nude": ART_NUDE_STYLES,
    }
    styles = mapping.get(category, {})
    item = styles.get(style_key, {})
    return item.get("prompt", "")


def get_yokai_prompt(yokai_key: str) -> dict:
    """获取妖怪的 prompt 和 scene"""
    return YOKAI_DICT.get(yokai_key, {})


def list_all_categories() -> list:
    """列出所有分类"""
    return [(c.key, c.cn) for c in ArtCategory]


def list_styles_by_category(category: str) -> dict:
    """列出某分类下的所有画风"""
    mapping = {
        "japanese": JAPANESE_STYLES,
        "gufeng": GUFENG_STYLES,
        "tang": TANG_STYLES,
        "art_nude": ART_NUDE_STYLES,
    }
    styles = mapping.get(category, {})
    return {k: v.get("name", k) for k, v in styles.items()}


def get_scroll_size(scroll_cn: str) -> dict:
    """获取画幅尺寸"""
    return SCROLL_SIZES.get(scroll_cn, SCROLL_SIZES["立轴"])


# ============================================================
# 自检
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  ArtForge 配置自检")
    print("=" * 60)

    print(f"\n📚 艺术分类 ({len(ArtCategory)} 个):")
    for key, cn in list_all_categories():
        print(f"  - {key}: {cn}")

    print(f"\n🖼️  画幅类型 ({len(ScrollType)} 个):")
    for s in ScrollType:
        print(f"  - {s.cn} ({s.ratio})")

    print(f"\n🎨 日式画风 ({len(JAPANESE_STYLES)} 个):")
    for k, v in JAPANESE_STYLES.items():
        print(f"  - {k}: {v['name']}")

    print(f"\n👹 妖怪图鉴 ({len(YOKAI_DICT)} 个):")
    for k, v in YOKAI_DICT.items():
        print(f"  - {k}: {v['name']}")

    print(f"\n🖌️  古风画风 ({len(GUFENG_STYLES)} 个):")
    for k, v in GUFENG_STYLES.items():
        print(f"  - {k}: {v['name']}")

    print(f"\n📜 源氏物语场景 ({len(GENJI_SCENES)} 个):")
    for k, v in GENJI_SCENES.items():
        print(f"  - {k}: {v['name']}")

    print(f"\n🏯 唐风画风 ({len(TANG_STYLES)} 个):")
    for k, v in TANG_STYLES.items():
        print(f"  - {k}: {v['name']}")

    print(f"\n🔖 题词格式 ({len(INSCRIPTION_CONFIG['formats'])} 种)")
    print(f"🔖 印章类型 ({len(INSCRIPTION_CONFIG['seal_types'])} 种)")
    print(f"🖼️  纸张纹理 ({len(AGING_CONFIG['paper_textures'])} 种)")
    print(f"🖼️  做旧效果 ({len(AGING_CONFIG['effects'])} 种)")

    print(f"\n🎨 传统颜料 ({len(MASTER_PALETTE['传统颜料'])} 色)")
    print(f"🎨 日本传统色 ({len(MASTER_PALETTE['日本传统色'])} 色)")

    print("\n" + "=" * 60)
    print("  ✅ 自检通过")
    print("=" * 60)