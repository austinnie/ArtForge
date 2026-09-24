# services/inscription_generator.py
"""
题词生成器 — 汉诗 / 和歌 / 俳句 / 题跋，三层降级

生成策略（优先级从高到低）：
  1. Agnes AI（有 AGNES_API_KEY 时）
  2. Pollinations 免费 chat（有网时，无需 Key）
  3. 内置诗句库（完全离线兜底）

用法:
    from services.inscription_generator import InscriptionGenerator

    ig = InscriptionGenerator()

    # 1. 只要文本
    text = ig.generate(theme="天狗", format="waka")

    # 2. 带元信息
    text, meta = ig.generate(theme="天狗", format="haiku", return_meta=True)
    # meta = {"format": "haiku", "theme": "天狗", "source": "agnes"}

    # 3. 指定用哪层（调试用）
    text = ig.generate(theme="天狗", format="waka", backend="library")
    text = ig.generate(theme="天狗", format="waka", backend="pollinations")

支持的 format: "wuyan"(五言) / "qiyan"(七言) / "waka"(和歌) /
                "haiku"(俳句) / "tiba"(题跋) / "auto"(随机)
支持的 theme:   天狗 / 河童 / 九尾狐 / 雪女 / 鬼 / 百鬼夜行 / ...（见 THEMES）
"""

from __future__ import annotations

import os
import random
import re
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union


# ============================================================
# 常量
# ============================================================

# ============================================================
# 路径修正（让 services/ 下的脚本能 import 项目根模块）
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:      # ← 新增
    sys.path.insert(0, str(PROJECT_ROOT))  # ← 新增


# services/inscription_generator.py 顶部

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# 加载 .env（让 os.getenv 能读到 API Key）
# ============================================================

try:
    from dotenv import load_dotenv
    _env_path = PROJECT_ROOT / ".env"
    if _env_path.exists():
        load_dotenv(_env_path)
    else:
        load_dotenv()   # 兜底：找当前目录
except ImportError:
    print("   ⚠️ 未安装 python-dotenv，.env 不会加载")
    
FORMATS = ["wuyan", "qiyan", "waka", "haiku", "tiba"]
FORMAT_NAMES_CN = {
    "wuyan": "五言",
    "qiyan": "七言",
    "waka": "和歌",
    "haiku": "俳句",
    "tiba": "题跋",
    "auto": "随机",
}

# 各体裁的期望字数（用于排版参考）
FORMAT_LENGTH = {
    "wuyan": 20,    # 4 句 × 5 字
    "qiyan": 28,    # 4 句 × 7 字
    "waka": 31,     # 5-7-5-7-7
    "haiku": 17,    # 5-7-5
    "tiba": 40,     # 灵活
}


# ============================================================
# 内置诗句库（离线兜底）
# 每个主题 × 每种体裁 2-3 首
# ============================================================

LIBRARY: Dict[str, Dict[str, List[str]]] = {

    "天狗": {
        "wuyan": [
            "鞍马山巅雪，长鼻破晓风。羽衣披月冷，独立万云空。",
            "赤面藏神威，振翅越千峰。山鬼皆低首，天狗啸苍穹。",
        ],
        "qiyan": [
            "鞍马山头月色寒，长鼻一啸动千山。羽衣拂落松间雪，独向苍茫云海间。",
            "赤面金睛势若神，羽翼遮天压乱云。山径石阶通绝顶，一声长啸万山闻。",
        ],
        "waka": [
            "鞍马の峰に 雪降り積もり 天狗舞う 長鼻の先 月を切るかな",
            "深山の霧 羽衣まとひ 天狗立つ 一声の風 木々を揺らせり",
        ],
        "haiku": [
            "天狗立つ 鞍马の雪 月を切る",
            "長鼻の 影や山霧 深く立つ",
        ],
        "tiba": [
            "鞍马山天狗者，传为护法之神，山民敬畏，四时祭祀不绝。",
            "此图写天狗踞山巅之态，长鼻赤面，羽衣飘然，远山如黛，云海苍茫。",
        ],
    },

    "河童": {
        "wuyan": [
            "碧水潜河童，头顶一勺清。绿鳞藏浅濑，拱手谢渔翁。",
            "河童戏浅滩，瓜顶戴清寒。夏夜萤火里，悠游水云间。",
        ],
        "qiyan": [
            "清流浅濑绿鳞生，头顶圆盘一勺清。夏夜萤火飞不尽，河童拱手谢渔翁。",
            "河畔垂柳映碧波，河童跃水弄圆荷。黄瓜掷尽无人问，独坐青石看星河。",
        ],
        "waka": [
            "清き瀬に 河童游びて 月映ゆる 頭の皿に 露の玉かな",
            "夏の夜の 川辺に河童 手を合わせ 胡瓜を供へ 静かに祈る",
        ],
        "haiku": [
            "河童来て 川面に月を 割りにけり",
            "胡瓜投げ 河童の頭 露を載せ",
        ],
        "tiba": [
            "河童者，水之精灵也，居于清流浅濑，好食胡瓜，与人相戏而不伤人。",
            "此图写河童戏水之景，碧波荡漾，垂柳依依，夏日清凉之气扑面而来。",
        ],
    },

    "九尾狐": {
        "wuyan": [
            "玉面映月光，九尾曳云长。一顾倾人国，千年隐山冈。",
            "白狐修九尾，月下化佳人。袖底藏春色，眉间隐妖氛。",
        ],
        "qiyan": [
            "千年修炼化人身，九尾摇曳月下春。一笑倾城终不悔，只缘曾许白头恩。",
            "玉面朱唇映月光，九尾如云曳地长。青丘山下桃花雨，一夜春风梦正香。",
        ],
        "waka": [
            "月の夜に 九尾の狐 化けにけり 袖の下より 春の風吹く",
            "青丘の 山に棲みけり 白き狐 千年の齢 人の姿に",
        ],
        "haiku": [
            "九尾舞う 月下の狐 人となる",
            "青丘の 雪に白き尾 光りけり",
        ],
        "tiba": [
            "九尾狐者，妖中之仙也，千年修得人身，其性媚而情真，古今传说多矣。",
            "此图写九尾狐化人之态，月华如水，九尾如云，妖气与仙气相杂，妙不可言。",
        ],
    },

    "雪女": {
        "wuyan": [
            "素衣临风雪，冰肌照夜寒。一吻封千壑，行人莫倚栏。",
            "雪女立苍茫，呼吸凝冰霜。回眸生百媚，转瞬即他乡。",
        ],
        "qiyan": [
            "素衣如雪立寒风，冰肌玉骨照夜空。一吻封喉人不返，只留残梦在孤灯。",
            "千山飞雪白皑皑，雪女悄从月下来。回眸一笑百媚生，转瞬无声归云海。",
        ],
        "waka": [
            "雪の夜に 白き衣の 女来て 息吹きかければ 凍りにけり",
            "山の奥 雪女立ちて 月を見る 声なき声に 魂凍ゆ",
        ],
        "haiku": [
            "雪女の 息吹に凍る 夜の月",
            "白き衣 雪に紛れて 消えにけり",
        ],
        "tiba": [
            "雪女者，雪中之妖也，形貌绝美而性寒，遇者多冻毙于风雪。",
            "此图写雪女临风之姿，素衣如雪，冰肌玉骨，冷艳之中含无限哀愁。",
        ],
    },

    "鬼": {
        "wuyan": [
            "赤面獠牙恶，铁棒扫秋风。地狱门开处，鬼火照夜红。",
            "鬼立罗生门，怒目视人寰。铁爪破长夜，一声震九天。",
        ],
        "qiyan": [
            "赤面獠牙立鬼门，铁棒横挥扫万军。地狱烈火腾空起，一声怒吼动乾坤。",
            "罗生门下鬼成群，月色如血照青磷。铁爪撕开长夜幕，孤魂野鬼尽惊奔。",
        ],
        "waka": [
            "羅生門に 鬼立ち騒ぎ 月赤し 鉄棒振りて 夜を裂きにけり",
            "地獄の 門開きけり 鬼の群れ 炎の中に 笑みを浮かべて",
        ],
        "haiku": [
            "鬼の門 赤き月夜に 鉄棒音",
            "羅生門 鬼火燃ゆると 人の泣く",
        ],
        "tiba": [
            "鬼者，恶之化身也，赤面獠牙，力大无穷，居地狱之门，为佛之护法亦有之。",
            "此图写鬼立罗生门之状，赤面怒目，铁棒在手，地狱烈火映月，森然可畏。",
        ],
    },

    "百鬼夜行": {
        "wuyan": [
            "百鬼夜行时，千灯乱月枝。行人闭门卧，不敢问归期。",
            "子夜百鬼出，灯笼映怪形。一夜游三界，人间梦正浓。",
        ],
        "qiyan": [
            "百鬼夜行灯火明，长街如昼怪形生。提灯童子前引路，伞怪跳跳随后行。",
            "夜半时分鬼出行，千灯万盏乱月明。人间闭户不敢语，只闻街上踏歌声。",
        ],
        "waka": [
            "夜半の 町に百鬼 行き交ひて 提灯の火 月を隠しけり",
            "百鬼の 行列長し 秋の夜 傘の下より 笑ひ声かな",
        ],
        "haiku": [
            "百鬼行く 提灯ひとつ 月隠れて",
            "秋の夜の 百鬼の列に 加はりたい",
        ],
        "tiba": [
            "百鬼夜行者，妖怪大游行也，每于子夜时分，群妖出行，人间闭户。",
            "此图写百鬼夜行之景，灯火辉煌，怪形毕现，提灯引路，伞怪随行，光怪陆离。",
        ],
    },

    "唐仕女": {
        "wuyan": [
            "云鬓花颜瘦，罗衣曳地长。一顾倾城色，春风满画堂。",
            "仕女倚画栏，团扇掩娇颜。牡丹开正盛，无意赏春寒。",
        ],
        "qiyan": [
            "云鬓花颜金步摇，罗衣曳地映春朝。回眸一笑百媚生，不羡天仙只羡娇。",
            "长安三月牡丹开，仕女簪花倚玉台。团扇轻摇风细细，不知春色为谁来。",
        ],
        "waka": [
            "唐の世の 美人立ちけり 牡丹咲く 團扇の影に 春を惜しめり",
            "羅衣の 袖に春風 花の顔 唐の都の 日は長かりけり",
        ],
        "haiku": [
            "唐美人 團扇に隠す 牡丹かな",
            "雲鬢に 牡丹の花を 挿しにけり",
        ],
        "tiba": [
            "唐仕女者，大唐盛世之丽人也，丰腴秀美，衣饰华贵，为一代之风范。",
            "此图写唐仕女游春之态，云鬓花颜，罗衣曳地，牡丹盛开，春意盎然。",
        ],
    },

    "飞天": {
        "wuyan": [
            "素手把琵琶，飞天下碧霄。彩云随袖舞，花雨落千朝。",
            "飞天凌空舞，飘带曳云霞。一声琵琶响，千佛共听法。",
        ],
        "qiyan": [
            "琵琶反弹舞碧空，彩带飘摇映日红。花雨纷飞千佛笑，敦煌壁上起仙风。",
            "飘带凌空若惊鸿，反弹琵琶向苍穹。一舞千年人不老，敦煌壁画永留踪。",
        ],
        "waka": [
            "敦煌の 壁に舞ひけり 天女ら 琵琶を抱へて 空に游ぶ",
            "彩帯の ひるがへる舞 花降りて 千仏の前 飛天笑めり",
        ],
        "haiku": [
            "飛天舞ふ 琵琶の音色 空に溶け",
            "彩帯曳き 天女の舞に 花降りぬ",
        ],
        "tiba": [
            "飞天天女者，敦煌壁画中之仙也，反弹琵琶，飘带凌空，为大唐艺术之绝唱。",
            "此图写飞天反弹琵琶之姿，飘带曳空，花雨纷飞，令人想见敦煌盛唐气象。",
        ],
    },
    "观月": {
        "wuyan": [
            "清宵悬皓月，庭树影婆娑。举盏遥相问，秋思入夜多。",
            "月满平安殿，清辉照玉栏。举杯人对影，不语共秋寒。",
        ],
        "waka": [
            "秋の夜の 月を眺めて 盃を 交はす人の 影やさしきかな",
            "月清し 御簾の内より 袖を出で 君と見る夜の 露の玉かな",
        ],
        "haiku": [
            "名月や 御殿の池に 影一つ",
            "月見する 袖の匂ひや 秋の暮",
        ],
        "tiba": [
            "此图写平安贵人对月之景，清辉满庭，诗酒相酬，物哀之情寓焉。",
        ],
    },
    "赏樱": {
        "wuyan": [
            "春风吹御苑，樱花落满衣。举杯还复落，不觉日西微。",
            "十二单袖里，藏得几枝樱。风来花似雪，人面共春明。",
        ],
        "waka": [
            "花の下に 立ちて眺むる 春の宵 袖に散りくる 桜の玉かな",
            "御所の庭 桜散りしく 十二単 袖に香りを 宿してぞ思ふ",
        ],
        "haiku": [
            "花見する 十二単の 袖ひらり",
            "春の宵 御所に散りしく 花吹雪",
        ],
        "tiba": [
            "此图写平安宫廷赏樱之景，十二单层叠，花落满衣，繁华无常之感寓焉。",
        ],
    },   

    "通用": {
        "wuyan": [
            "淡墨无声染，青山半隐痕。松风伴鹤去，留白见天宽。",
            "纸上烟云起，笔端丘壑生。不知身在此，疑是入山行。",
            "墨色分浓淡，山河入卷来。一舟横野渡，烟雨任徘徊。",
        ],
        "qiyan": [
            "淡墨无声染素笺，青山半隐墨痕间。松风伴鹤归云外，留白处见天地宽。",
            "笔落惊风雨满堂，墨分五色意悠长。江山不尽丹青里，一卷春秋入锦章。",
            "烟云供养写溪山，笔底苍茫墨未干。莫道丹青无觅处，此身已在画图间。",
        ],
        "waka": [
            "筆の先 墨の香りに 誘はれて 心のままに 山河を描く",
            "白き紙 墨の一滴 落ちる時 無限の世界 ひらりと生まる",
            "岩に松 烟に隠れし 山の端に 墨の一滴 秋の風吹く",
        ],
        "haiku": [
            "筆を取る 墨の香りや 春の宵",
            "白紙に 一滴の墨 山河かな",
            "松風や 墨の香りに 秋深し",
        ],
        "tiba": [
            "此图写东方山水之景，笔墨精妙，气韵生动，观之神游物外。",
            "画家以心运笔，以墨写意，咫尺之间，尽显千里之势。",
            "一卷丹青，写尽人间丘壑。几笔淡墨，藏得天地无穷。",
        ],
    },    
}

# 主题别名 → 标准 key
THEME_ALIAS = {
    "tengu": "天狗",
    "kappa": "河童",
    "kitsune": "九尾狐",
    "yuki_onna": "雪女",
    "yuki": "雪女",
    "oni": "鬼",
    "hyakki": "百鬼夜行",
    "hyakki_yagyo": "百鬼夜行",
    "tang_beauty": "唐仕女",
    "tang": "唐仕女",
    "dunhuang": "飞天",
    "feitian": "飞天",
}

THEMES = list(LIBRARY.keys())


# ============================================================
# 提示词模板（给 LLM 用）
# ============================================================

PROMPT_TEMPLATES = {
    "wuyan": (
        "请以「{theme}」为题，写一首五言绝句（4 句，每句 5 字，共 20 字）。"
        "要求：意境契合东方古典美学，用词典雅，避免现代词汇。"
        "直接输出诗句，不要标题，不要解释。"
    ),
    "qiyan": (
        "请以「{theme}」为题，写一首七言绝句（4 句，每句 7 字，共 28 字）。"
        "要求：意境契合东方古典美学，用词典雅，避免现代词汇。"
        "直接输出诗句，不要标题，不要解释。"
    ),
    "waka": (
        "请以「{theme}」为题，写一首和歌（5-7-5-7-7 音，共 31 音）。"
        "可以用日文或中文，风格要古典、含蓄。"
        "直接输出和歌，不要标题，不要解释。"
    ),
    "haiku": (
        "请以「{theme}」为题，写一首俳句（5-7-5 音，共 17 音）。"
        "要求：含蓄、有意象、留白。"
        "直接输出俳句，不要标题，不要解释。"
    ),
    "tiba": (
        "请以「{theme}」为题，写一段题跋（40-60 字的散文），"
        "用于题在一幅东方艺术画作上。要求：文言风格，点明画中意境。"
        "直接输出题跋，不要标题，不要解释。"
    ),
}

# 「通用」主题的专属模板（不写"以通用为题"）
PROMPT_TEMPLATES_GENERIC = {
    "wuyan": (
        "请写一首五言绝句（4 句，每句 5 字，共 20 字），"
        "不指定具体主题，写东方山水意境，"
        "可用于题在一幅东方水墨/工笔画作上。"
        "要求：意境深远，用词典雅，避免现代词汇。"
        "直接输出诗句，不要标题，不要解释。"
    ),
    "qiyan": (
        "请写一首七言绝句（4 句，每句 7 字，共 28 字），"
        "不指定具体主题，写东方山水意境，"
        "可用于题在一幅东方画作上。"
        "要求：意境深远，用词典雅，避免现代词汇。"
        "直接输出诗句，不要标题，不要解释。"
    ),
    "waka": (
        "请写一首和歌（5-7-5-7-7 音，共 31 音），"
        "不指定具体主题，写东方自然意境，"
        "可用于题在一幅东方画作上。"
        "风格古典、含蓄，用日文。"
        "直接输出和歌，不要标题，不要解释。"
    ),
    "haiku": (
        "请写一首俳句（5-7-5 音，共 17 音），"
        "不指定具体主题，写东方自然意象，"
        "可用于题在一幅东方画作上。"
        "要求：含蓄、有意象、留白。"
        "直接输出俳句，不要标题，不要解释。"
    ),
    "tiba": (
        "请写一段题跋（40-60 字的散文），"
        "不指定具体主题，写东方山水意境，"
        "用于题在一幅东方画作上。"
        "要求：文言风格，点明画中意境。"
        "直接输出题跋，不要标题，不要解释。"
    ),
}

SYSTEM_PROMPT = (
    "你是一位精通东方古典文学的诗人，擅长汉诗、和歌、俳句、题跋。"
    "你的作品典雅、含蓄、有意境。"
    "和歌请严格按 5-7-5-7-7 音写作，用现代日语可读的古典表达，"
    "避免生僻的古语变体（如「隠るる」）。"
    "只输出正文，不加任何解释或标注。"
)


# ============================================================
# InscriptionGenerator
# ============================================================

class InscriptionGenerator:
    """题词生成器（三层降级）"""

    def __init__(
        self,
        agnes_engine=None,
        seed: Optional[int] = None,
    ):
        """
        Args:
            agnes_engine: 可选的 AgnesEngine 实例（复用已有引擎）
            seed:         随机种子（library 兜底时可复现）
        """
        self.agnes = agnes_engine
        self.seed = seed
        self._rng = random.Random(seed)
        self._pollinations = None   # 懒加载

    # ------------------------------------------------------------
    # 主接口
    # ------------------------------------------------------------

    def generate(
        self,
        theme: str = "天狗",
        format: str = "auto",
        backend: str = "auto",
        return_meta: bool = False,
    ) -> Union[str, Tuple[str, Dict]]:
        """
        生成题词。

        Args:
            theme:    主题（中文或英文 key，见 THEME_ALIAS）
            format:   wuyan/qiyan/waka/haiku/tiba/auto
            backend:  auto/agnes/pollinations/library
            return_meta: 是否返回 (text, meta)

        Returns:
            text 或 (text, meta)
        """
        # 1. 规范化
        theme_std = self._normalize_theme(theme)
        fmt = self._normalize_format(format)

        # 2. 选 backend
        chosen, text = self._dispatch(theme_std, fmt, backend)

        # 3. 清理文本
        text = self._clean(text)

        meta = {
            "theme": theme_std,
            "format": fmt,
            "format_cn": FORMAT_NAMES_CN.get(fmt, fmt),
            "source": chosen,
            "length": len(text),
            "expected_length": FORMAT_LENGTH.get(fmt, 0),
        }

        return (text, meta) if return_meta else text

    # ------------------------------------------------------------
    # 分发
    # ------------------------------------------------------------

    def _dispatch(
        self,
        theme: str,
        fmt: str,
        backend: str,
    ) -> Tuple[str, str]:
        """
        按 backend 策略分发。返回 (source, text)。
        """
        backend = backend.lower()

        # 手动指定
        if backend == "library":
            return ("library", self._from_library(theme, fmt))
        if backend == "agnes":
            txt = self._from_agnes(theme, fmt)
            if txt:
                return ("agnes", txt)
            print("   ⚠️ Agnes 生成失败，降级到 library")
            return ("library", self._from_library(theme, fmt))
        if backend == "pollinations":
            txt = self._from_pollinations(theme, fmt)
            if txt:
                return ("pollinations", txt)
            print("   ⚠️ Pollinations 生成失败，降级到 library")
            return ("library", self._from_library(theme, fmt))

        # auto：agnes → pollinations → library
        if backend == "auto":
            txt = self._from_agnes(theme, fmt)
            if txt:
                return ("agnes", txt)
            txt = self._from_pollinations(theme, fmt)
            if txt:
                return ("pollinations", txt)
            return ("library", self._from_library(theme, fmt))

        print(f"   ⚠️ 未知 backend '{backend}'，使用 auto")
        return self._dispatch(theme, fmt, "auto")

    # ------------------------------------------------------------
    # Layer 1: Agnes
    # ------------------------------------------------------------

    def _from_agnes(self, theme: str, fmt: str) -> Optional[str]:
        """用 Agnes chat 生成。失败返回 None。"""
        if self.agnes is None:
            # 尝试从环境变量创建
            key = os.getenv("AGNES_API_KEY")
            if not key:
                return None
            try:
                from api_engines.agnes import AgnesEngine
                self.agnes = AgnesEngine(
                    api_key=key,
                    base_url=os.getenv("AGNES_BASE_URL"),
                    image_model=os.getenv("AGNES_IMAGE_MODEL"),
                )
            except Exception as e:
                print(f"   ⚠️ 初始化 Agnes 失败: {e}")
                return None

        # 选模板：通用主题用专属模板
        if theme == "通用":
            template = PROMPT_TEMPLATES_GENERIC.get(fmt, PROMPT_TEMPLATES_GENERIC["waka"])
            prompt = template
        else:
            template = PROMPT_TEMPLATES.get(fmt, PROMPT_TEMPLATES["waka"])
            prompt = template.format(theme=theme)

        try:
            print(f"   🤖 Agnes 生成题词: {theme} / {FORMAT_NAMES_CN.get(fmt, fmt)}")
            text = self.agnes.chat_simple(prompt, system_prompt=SYSTEM_PROMPT)
            if text and len(text.strip()) > 4:
                return text.strip()
            print(f"   ⚠️ Agnes 返回空或过短: {repr(text)[:80]}")
        except Exception as e:
            print(f"   ⚠️ Agnes 调用失败: {type(e).__name__}: {e}")

        return None

    # ------------------------------------------------------------
    # Layer 2: Pollinations 免费 chat
    # ------------------------------------------------------------

    def _from_pollinations(self, theme: str, fmt: str) -> Optional[str]:
        """用 Pollinations chat 生成。失败返回 None。"""
        if self._pollinations is None:
            try:
                from api_engines.pollinations import PollinationsEngine
                self._pollinations = PollinationsEngine(
                    api_key=os.getenv("POLLINATIONS_API_KEY"),
                )
            except Exception as e:
                print(f"   ⚠️ 初始化 Pollinations 失败: {e}")
                return None

        # 选模板：通用主题用专属模板
        if theme == "通用":
            template = PROMPT_TEMPLATES_GENERIC.get(fmt, PROMPT_TEMPLATES_GENERIC["waka"])
            prompt = template
        else:
            template = PROMPT_TEMPLATES.get(fmt, PROMPT_TEMPLATES["waka"])
            prompt = template.format(theme=theme)

        try:
            print(f"   🌐 Pollinations 生成题词: {theme} / {FORMAT_NAMES_CN.get(fmt, fmt)}")
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ]
            text = self._pollinations.chat(messages, model="openai")
            if text and len(text.strip()) > 4:
                return text.strip()
        except Exception as e:
            print(f"   ⚠️ Pollinations 调用失败: {e}")

        return None

    # ------------------------------------------------------------
    # Layer 3: 内置诗句库
    # ------------------------------------------------------------

    def _from_library(self, theme: str, fmt: str) -> str:
        """从内置库随机抽。"""
        print(f"   📚 从内置库抽取题词: {theme} / {FORMAT_NAMES_CN.get(fmt, fmt)}")

        # 主题不在库中 → 用天狗兜底
        if theme not in LIBRARY:
            print(f"   ⚠️ 主题 '{theme}' 不在库中，使用「天狗」兜底")
            theme = "天狗"

        bucket = LIBRARY[theme]
        if fmt not in bucket or not bucket[fmt]:
            # 体裁缺失 → 换一个
            fallback = next((f for f in FORMATS if bucket.get(f)), None)
            if fallback is None:
                return "（题词暂缺）"
            print(f"   ⚠️ 体裁 '{fmt}' 缺失，改用 '{fallback}'")
            fmt = fallback

        return self._rng.choice(bucket[fmt])

    # ------------------------------------------------------------
    # 工具
    # ------------------------------------------------------------

    @staticmethod
    def _normalize_theme(theme: str) -> str:
        """英文 key / 别名 → 标准中文。"""
        if not theme:
            return "天狗"
        t = theme.strip()
        if t in LIBRARY:
            return t
        if t.lower() in THEME_ALIAS:
            return THEME_ALIAS[t.lower()]
        return t

    def _normalize_format(self, fmt: str) -> str:
        """format 规范化，auto 随机。"""
        if not fmt:
            return "waka"
        f = fmt.strip().lower()
        if f == "auto":
            return self._rng.choice(FORMATS)
        if f not in FORMATS:
            print(f"   ⚠️ 未知体裁 '{fmt}'，使用 waka")
            return "waka"
        return f

    @staticmethod
    def _clean(text: str) -> str:
        """去掉 LLM 可能带的前缀/引号/解释。"""
        if not text:
            return ""

        t = text.strip()

        # 去掉 markdown 引号包裹
        t = t.strip('"').strip("'").strip("“”").strip("‘’")

        # 去掉常见前缀
        for prefix in [
            "题词：", "题词:", "诗句：", "诗句:",
            "和歌：", "和歌:", "俳句：", "俳句:",
            "题跋：", "题跋:", "输出：", "输出:",
        ]:
            if t.startswith(prefix):
                t = t[len(prefix):].strip()

        # 去掉 markdown 代码块
        t = re.sub(r"^```[a-zA-Z]*\s*", "", t)
        t = re.sub(r"\s*```$", "", t)

        # 去掉行首的 "1." "2." 等编号
        lines = []
        for line in t.split("\n"):
            line = re.sub(r"^\s*\d+[.、)]\s*", "", line)
            lines.append(line.strip())
        t = "\n".join(l for l in lines if l)

        return t.strip()

    # ------------------------------------------------------------
    # 批量 / 列表
    # ------------------------------------------------------------

    def list_themes(self) -> List[str]:
        """返回内置库支持的主题。"""
        return list(THEMES)

    def list_formats(self) -> Dict[str, str]:
        """返回体裁 → 中文名。"""
        return dict(FORMAT_NAMES_CN)

    def preview(self, theme: str = "天狗") -> Dict[str, List[str]]:
        """预览某主题的所有体裁（library 层）。"""
        theme_std = self._normalize_theme(theme)
        return LIBRARY.get(theme_std, {})


# ============================================================
# 自检
# ============================================================

if __name__ == "__main__":
    print("=" * 70)
    print("  InscriptionGenerator 自检")
    print("=" * 70)

    ig = InscriptionGenerator(seed=42)

    print(f"\n📚 支持主题 ({len(THEMES)}): {', '.join(THEMES)}")
    print(f"📐 支持体裁 ({len(FORMATS)}): {', '.join(FORMAT_NAMES_CN[f] for f in FORMATS)}")

    print("\n" + "-" * 70)
    print("  【Layer 3 内置库】离线兜底")
    print("-" * 70)
    for theme in ["天狗", "河童", "九尾狐", "雪女", "鬼"]:
        for fmt in ["wuyan", "waka", "haiku"]:
            text = ig.generate(theme=theme, format=fmt, backend="library")
            print(f"\n  [{theme} / {FORMAT_NAMES_CN[fmt]}]")
            print(f"  {text}")

    print("\n" + "-" * 70)
    print("  【别名解析】")
    print("-" * 70)
    for alias in ["tengu", "kappa", "kitsune", "dunhuang", "tang_beauty"]:
        text, meta = ig.generate(theme=alias, format="haiku",
                                  backend="library", return_meta=True)
        print(f"  {alias:12s} → {meta['theme']:6s} | {text}")

    print("\n" + "-" * 70)
    print("  【auto 模式】探测可用 backend")
    print("-" * 70)
    text, meta = ig.generate(theme="天狗", format="waka",
                              backend="auto", return_meta=True)
    print(f"\n  source = {meta['source']}")
    print(f"  题词   = {text}")
    print(f"  长度   = {meta['length']} (期望 {meta['expected_length']})")

    print("\n" + "-" * 70)
    print("  【可复现性】同 seed 同主题")
    print("-" * 70)
    ig1 = InscriptionGenerator(seed=7)
    ig2 = InscriptionGenerator(seed=7)
    a = ig1.generate("天狗", "waka", backend="library")
    b = ig2.generate("天狗", "waka", backend="library")
    print(f"\n  {'✅ 一致' if a == b else '❌ 不一致'}")

    print("\n" + "=" * 70)
    print("  ✅ 自检完成")
    print("=" * 70)