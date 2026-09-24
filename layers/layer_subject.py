# layers/layer_subject.py
"""
第 1 层：主体

包含：
  - 妖怪主体（天狗、河童、九尾狐、雪女、鬼…）
  - 人物主体（艺伎、武士、唐仕女、平安贵妇…）
  - 动物/花鸟（鹤、鲤、猫、樱…）
  - 抽象主体（山水、庭院、屏风…）

格式：英文 prompt 短语（逗号分隔）
"""

LAYER = [
    # ==================== 妖怪 ====================
    "a fierce tengu with long red nose, feathered wings, "
    "yamabushi mountain hermit attire, holding a hauchiwa fan",

    "a mischievous kappa with green scaly skin, "
    "a water dish on its head, turtle shell, webbed hands",

    "a nine-tailed kitsune fox spirit with snow-white fur, "
    "golden glowing eyes, mystical aura, elegant posture",

    "a pale yuki-onna snow woman with long black hair, "
    "blue lips, white kimono, ethereal and tragic beauty",

    "a fierce oni demon with red skin, sharp horns, "
    "tiger-skin loincloth, wielding a kanabo iron club",

    "a mysterious kitsune-bi fox fire, floating blue flames "
    "in a dark forest, a procession of fox spirits",

    "a night parade of one hundred yokai, "
    "hyakki yagyo, countless demons marching with lanterns",

    "a fox wedding procession, kitsune no yomeiri, "
    "fox spirits in human form under light rain and sunbeams",

    "a noppera-bo faceless ghost, smooth blank face, "
    "woman in kimono, unsettling and eerie",

    "a rokurokubi long-necked woman, stretching her neck "
    "at night in an Edo-period bedroom",

    # ==================== 日本人物 ====================
    "an elegant geisha in a lavishly embroidered kimono, "
    "elaborate kanzashi hair ornaments, white makeup, "
    "holding a folding fan, refined gesture",

    "a noble samurai in full armor, kabuto helmet with crest, "
    "katana at his side, standing with quiet dignity",

    "a beautiful maiko apprentice geisha, "
    "long trailing obi, cherry blossom hairpin, "
    "graceful kneeling posture",

    "a Heian-period court lady in twelve-layer junihitoe, "
    "long black hair, fan in hand, seated on a veranda",

    "a noble Heian courtier in sokutai robes and eboshi hat, "
    "playing a flute beneath a full moon",

    # ==================== 唐风人物 ====================
    "a plump Tang dynasty court lady, high bun with floral "
    "hairpin, colorful silk dress, round gentle face, "
    "holding a round fan",

    "an elegant Tang dynasty palace lady playing a pipa, "
    "flowing silk sleeves, gold ornaments, refined elegance",

    "a Dunhuang flying apsara, feitian, celestial dancer, "
    "flowing ribbons, lotus flowers, Buddhist mural style",

    # ==================== 动物 / 花鸟 ====================
    "a red-crowned crane standing on one leg, "
    "long curved neck, elegant posture, minimal background",

    "a koi fish swimming among lotus leaves, "
    "flowing fins, rippling water, graceful motion",

    "a white fox sitting quietly under a full moon, "
    "nine faint tails visible, mystical atmosphere",

    "a pair of mandarin ducks in a lotus pond, "
    "symbol of love and fidelity, delicate brushwork",

    "a tiger walking through bamboo, powerful stance, "
    "traditional ink painting style, muscular form",

    "a playful cat sitting on a veranda, "
    "watching cherry blossoms fall, peaceful moment",

    # ==================== 山水 / 场景主体 ====================
    "a serene mountain landscape with mist rolling "
    "between layered peaks, a small pavilion on a cliff",

    "a classic Chinese scholar's garden, "
    "rockery, pond, bamboo, moon gate, quiet atmosphere",

    "a folding screen showing four seasons, "
    "gold leaf background, Rimpa-style decorative motifs",

    "a cherry blossom tree in full bloom, "
    "petals falling like snow, branches silhouetted",

    "a snow-covered pine forest at dusk, "
    "solitary figure walking in the distance",

    "a red torii gate pathway leading up a mountain, "
    "stone lanterns, moss-covered steps, misty morning",

    "a bamboo grove in light rain, "
    "vertical stalks, dripping leaves, quiet sound",

    "a lotus pond in summer, "
    "large round leaves, pink blossoms, dragonflies hovering",

    # ==================== 抽象 / 极简 ====================
    "a single brushstroke of black ink forming a mountain silhouette, "
    "extreme minimalism, vast negative space",

    "a circular moon painted in gold leaf, "
    "framed by thin clouds, contemplative mood",

    "a lone pine tree on a rocky cliff, "
    "windswept branches, stormy sky behind",

    "a single plum blossom branch, "
    "red blossoms emerging from dark ink trunk, "
    "early spring, snow on the ground",
]