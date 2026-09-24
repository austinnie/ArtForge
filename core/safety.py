# core/safety.py
"""
ArtForge 安全过滤模块
职责：
- 关键词黑名单（现代色情、未成年人、暴力等）
- 艺术豁免规则（浮世绘春画、能剧面具、花魁等传统题材放行）
- 年龄/身份检测提示（非严格识别，仅提示）

设计原则：
- 默认严格，但为传统东方艺术留豁免通道
- 豁免规则基于「主题 + 画风 + 关键词」组合判断
"""
from __future__ import annotations
import re
from typing import Tuple, List, Optional


# ============================================================
# 黑名单（现代色情 / 未成年人 / 极端暴力）
# ============================================================
BLOCK_PATTERNS = [
    # 未成年人相关
    r"\b(underage|minor|child|young girl|young boy|loli|shota)\b",
    r"(未成年|幼女|幼男|萝莉|正太|儿童\s*(色情|裸体))",
    # 现代色情（非艺术）
    r"\b(porn|xxx|hentai|explicit sex|hardcore)\b",
    r"(色情片|成人视频|援交|卖淫)",
    # 极端暴力
    r"\b(gore|extreme violence|torture porn)\b",
    r"(血腥\s*虐杀|虐童)",
    # 真实人物（避免肖像权）
    r"\b(taylor swift|emma watson|scarlett johansson)\b",
]

# ============================================================
# 艺术豁免关键词（传统东方美学范畴）
# ============================================================
ART_EXEMPTION_SUBJECTS = {
    # 浮世绘春画（传统艺术）
    "shunga", "spring picture", "ukiyo-e shunga", "erotic ukiyo-e",
    "春画", "浮世绘春画", "枕绘",
    # 能剧面具
    "noh mask", "noh theater mask", "能面", "能剧面具",
    # 花魁（传统艺伎）
    "oiran", "courtesan", "花魁", "太夫",
    # 传统沐浴/裸体艺术
    "bijin-ga", "beautiful women", "美人画",
    # 佛教艺术（半裸神像）
    "apsara", "feitian", "飞天", "天女",
    "bodhisattva", "菩萨", "观音",
}

ART_EXEMPTION_STYLES = {
    "ukiyo-e", "浮世绘",
    "nihonga", "日本画",
    "sumi-e", "水墨",
    "yamato-e", "大和绘",
    "dunhuang", "敦煌",
    "tang dynasty", "唐代",
    "heian", "平安",
}


class SafetyFilter:
    """安全过滤器"""

    def __init__(self, strict: bool = True):
        self.strict = strict
        self._compiled = [re.compile(p, re.IGNORECASE) for p in BLOCK_PATTERNS]

    def check(self, prompt: str, style: str = "", subject: str = "") -> Tuple[bool, str]:
        """
        检查 prompt 是否安全
        Returns: (is_safe, reason)
        """
        text = f"{prompt} {style} {subject}".lower()

        # 1. 先检查是否命中艺术豁免
        if self._is_art_exemption(text):
            # 豁免后仍需检查硬性黑名单（未成年人等）
            hard_block = self._check_hard_block(text)
            if hard_block:
                return False, f"🚫 硬黑名单命中（艺术豁免不适用）: {hard_block}"
            return True, "✅ 艺术豁免通过"

        # 2. 常规黑名单检查
        for pat in self._compiled:
            m = pat.search(text)
            if m:
                return False, f"🚫 命中黑名单: {m.group(0)}"

        return True, "✅ 通过"

    def _is_art_exemption(self, text: str) -> bool:
        """判断是否属于艺术豁免范畴"""
        # 必须同时满足：主题豁免 + 画风豁免
        has_subject = any(kw in text for kw in ART_EXEMPTION_SUBJECTS)
        has_style = any(kw in text for kw in ART_EXEMPTION_STYLES)
        return has_subject and has_style

    def _check_hard_block(self, text: str) -> Optional[str]:
        """硬黑名单（即使艺术豁免也不放行）"""
        hard_patterns = [
            re.compile(r"\b(underage|minor|child|loli|shota)\b", re.I),
            re.compile(r"(未成年|幼女|幼男|萝莉|正太)"),
        ]
        for pat in hard_patterns:
            m = pat.search(text)
            if m:
                return m.group(0)
        return None

    def sanitize(self, prompt: str) -> str:
        """清理 prompt 中的敏感词（简单替换）"""
        result = prompt
        # 这里只做简单处理，实际可根据需要扩展
        return result


# ============================================================
# 便捷函数
# ============================================================
_default_filter = SafetyFilter()

def check_safety(prompt: str, style: str = "", subject: str = "") -> Tuple[bool, str]:
    """全局安全检查"""
    return _default_filter.check(prompt, style, subject)


# ============================================================
# 自检
# ============================================================
if __name__ == "__main__":
    print("=" * 70)
    print("  SafetyFilter 自检")
    print("=" * 70)

    sf = SafetyFilter()

    tests = [
        # (prompt, style, subject, 预期)
        ("beautiful woman in kimono", "ukiyo-e", "bijin-ga", True),
        ("ukiyo-e shunga traditional", "ukiyo-e", "shunga", True),
        ("noh mask demon", "nihonga", "noh mask", True),
        ("飞天 敦煌壁画", "dunhuang", "apsara", True),
        ("underage girl", "photography", "", False),
        ("explicit sex scene", "", "", False),
        ("花魁 浮世绘", "ukiyo-e", "oiran", True),
        ("萝莉 色情", "", "", False),  # 硬黑名单，即使有豁免也拦
    ]

    for prompt, style, subject, expected in tests:
        ok, reason = sf.check(prompt, style, subject)
        status = "✅" if ok == expected else "❌"
        print(f"{status} [{prompt[:30]:30s}] → {reason}")

    print("=" * 70)