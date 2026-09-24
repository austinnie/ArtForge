# core/prompt_builder.py
"""
ArtForge 6 层提示词组合器

职责：
  - 加载 7 层短语库
  - 支持随机 / 索引 / 预设 三种组合模式
  - 智能 Token 截断（按层优先级保留）
  - 支持从 presets/ 加载预设并覆盖指定层

用法：
    from core.prompt_builder import PromptBuilder

    # 1. 随机组合
    builder = PromptBuilder()
    prompt = builder.compose_random()

    # 2. 索引组合（可复现）
    prompt = builder.compose_by_index(42)

    # 3. 预设组合
    prompt, detail = builder.compose_preset(
        "tengu", category="yokai", return_detail=True,
    )
"""

import re
import random
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union


# ============================================================
# 路径常量
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PRESETS_DIR = PROJECT_ROOT / "presets"


# ============================================================
# 尝试导入 tiktoken（精确计数）
# ============================================================

try:
    import tiktoken
    _TIKTOKEN_AVAILABLE = True
except ImportError:
    _TIKTOKEN_AVAILABLE = False


# ============================================================
# 默认负面提示词
# ============================================================

DEFAULT_NEGATIVE = (
    "worst quality, low quality, blurry, ugly, deformed, "
    "bad anatomy, bad hands, extra fingers, missing fingers, "
    "watermark, signature (except traditional seal), text overlay, "
    "modern logo, photograph of a screen, jpeg artifacts, "
    "oversaturated, neon colors unless intended, "
    "3d render, cgi, plastic look"
)


# ============================================================
# PromptBuilder 类
# ============================================================

class PromptBuilder:
    """6 层提示词组合器"""

    # 层级顺序（从 layers 模块导入，避免重复定义）
    from layers import LAYER_ORDER, LAYER_NAMES_CN, LAYER_PRIORITY

    def __init__(self, layers: Optional[Dict[str, List[str]]] = None):
        """
        初始化组合器。

        Args:
            layers: 自定义层字典。不传则自动从 layers 包加载。
        """
        if layers is None:
            from layers import load_all_layers
            layers = load_all_layers()

        self.layers = layers
        self._tokenizer = None

        # 初始化 tokenizer
        if _TIKTOKEN_AVAILABLE:
            try:
                self._tokenizer = tiktoken.get_encoding("cl100k_base")
            except Exception:
                self._tokenizer = None

        self._validate()

    # ---------- 校验 ----------

    def _validate(self):
        """检查各层是否有内容。"""
        for key in self.LAYER_ORDER:
            if key not in self.layers or not self.layers[key]:
                print(f"   ⚠️ 层 '{key}' 为空")

    # ---------- Token 计数与截断 ----------

    def _count_tokens(self, text: str) -> int:
        """计算文本的 token 数。"""
        if not text:
            return 0
        if self._tokenizer:
            return len(self._tokenizer.encode(text))
        # fallback：粗略估算 1 token ≈ 4 字符
        return len(text) // 4

    def _truncate_to_limit(
        self,
        prompt: str,
        max_tokens: int = 77,
        kept_layers: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        智能截断到指定 token 数。

        策略（两级）：
          1. 按层优先级降序，从高到低加入
          2. 整层放不下 → 逐短语加入
          3. 某层一个短语都放不下 → 停止（后面的层更不重要）
          4. 最后按 LAYER_ORDER 重排拼装（保持语序）

        Args:
            prompt: 完整 prompt
            max_tokens: token 上限
            kept_layers: 各层已选中的短语 {layer_key: phrase}

        Returns:
            截断后的 prompt
        """
        if self._count_tokens(prompt) <= max_tokens:
            return prompt

        # 无明细：暴力从尾部裁
        if not kept_layers:
            parts = prompt.split(", ")
            while len(parts) > 1:
                parts.pop()
                if self._count_tokens(", ".join(parts)) <= max_tokens:
                    return ", ".join(parts)
            return prompt[: max_tokens * 4]

        # 按优先级降序（重要在前）
        ordered = sorted(
            kept_layers.items(),
            key=lambda kv: self.LAYER_PRIORITY.get(kv[0], 0),
            reverse=True,
        )

        # 记录每层实际保留的短语片段
        kept_phrases: Dict[str, List[str]] = {}

        for key, value in ordered:
            if not value or not value.strip():
                continue

            # 已保留的所有短语
            existing = [p for phrases in kept_phrases.values() for p in phrases]

            # 尝试加入整层
            trial = existing + [value]
            if self._count_tokens(", ".join(trial)) <= max_tokens:
                kept_phrases[key] = [value]
                continue

            # 整层放不下 → 逐短语加入
            sub_phrases = [p.strip() for p in value.split(",") if p.strip()]
            added: List[str] = []
            for sp in sub_phrases:
                trial = existing + added + [sp]
                if self._count_tokens(", ".join(trial)) <= max_tokens:
                    added.append(sp)
                else:
                    break

            if added:
                kept_phrases[key] = added
            else:
                # 这一层完全放不下，后面的层更不重要，停止
                break

        # 按 LAYER_ORDER 重排拼装（保持语序）
        final_parts: List[str] = []
        for key in self.LAYER_ORDER:
            if key in kept_phrases:
                final_parts.extend(kept_phrases[key])

        return ", ".join(final_parts)
        
    # ---------- 3 种组合模式 ----------

    def compose_random(
        self,
        max_tokens: Optional[int] = None,
        return_detail: bool = False,
    ) -> Union[str, Tuple[str, Dict[str, str]]]:
        """
        完全随机组合：每层随机抽一个短语。

        Args:
            max_tokens: token 上限（None 表示不限制）
            return_detail: 是否同时返回各层明细

        Returns:
            prompt 或 (prompt, detail)
        """
        detail: Dict[str, str] = {}
        for key in self.LAYER_ORDER:
            options = self.layers.get(key, [])
            if options:
                detail[key] = random.choice(options)

        full = self._join(detail)

        if max_tokens and max_tokens > 0:
            full = self._truncate_to_limit(full, max_tokens, detail)

        return (full, detail) if return_detail else full

    def compose_by_index(
        self,
        index: int,
        max_tokens: Optional[int] = None,
        return_detail: bool = False,
    ) -> Union[str, Tuple[str, Dict[str, str]]]:
        """
        按索引组合：每层用 index 对该层长度取模。

        同一 index 每次调用结果相同（可复现）。

        Args:
            index: 组合索引（任意整数）
            max_tokens: token 上限
            return_detail: 是否返回明细

        Returns:
            prompt 或 (prompt, detail)
        """
        detail: Dict[str, str] = {}
        for key in self.LAYER_ORDER:
            options = self.layers.get(key, [])
            if options:
                detail[key] = options[index % len(options)]

        full = self._join(detail)

        if max_tokens and max_tokens > 0:
            full = self._truncate_to_limit(full, max_tokens, detail)

        return (full, detail) if return_detail else full

    def compose_preset(
        self,
        preset_name: str,
        category: Optional[str] = None,
        max_tokens: Optional[int] = None,
        return_detail: bool = False,
        subject_override: Optional[str] = None,
        scene_override: Optional[str] = None,
        style_override: Optional[str] = None,
        lighting_override: Optional[str] = None,
        composition_override: Optional[str] = None,
        inscription_override: Optional[str] = None,
        quality_override: Optional[str] = None,
    ) -> Union[str, Tuple[str, Dict[str, str]]]:
        """
        预设组合：加载 presets/<category>/<name>.py，
        用预设里的 `layers` 覆盖对应层，然后随机组合。

        预设文件格式：
            PRESET = {
                "name": "天狗",
                "category": "yokai",
                "layers": {
                    "subject": ["..."],          # 覆盖 subject 层的候选
                    "scene": ["..."],            # 覆盖 scene 层
                    "style": ["..."],            # 覆盖 style 层
                    "lighting": ["..."],
                    "composition": ["..."],
                    "inscription": ["..."],
                    "quality": ["..."],
                },
            }

        Args:
            preset_name: 预设文件名（不含 .py）
            category: 预设分类（japanese / yokai / gufeng / genji / tang / art_nude）
                      不传时自动搜索所有分类
            max_tokens: token 上限
            return_detail: 是否返回明细
            各层 override: 强制指定某层的候选（单条），优先级高于预设

        Returns:
            prompt 或 (prompt, detail)
        """
        preset = self.load_preset(preset_name, category=category)
        if not preset:
            print(f"   ⚠️ 未找到预设: {category or '*'}/{preset_name}")
            print(f"   → 回退到随机组合")
            return self.compose_random(max_tokens=max_tokens, return_detail=return_detail)

        # 从预设的 layers 覆盖
        merged = self._merge_preset(preset.get("layers", {}))

        # 应用单条 override
        overrides = {
            "subject": subject_override,
            "scene": scene_override,
            "style": style_override,
            "lighting": lighting_override,
            "composition": composition_override,
            "inscription": inscription_override,
            "quality": quality_override,
        }
        for key, val in overrides.items():
            if val:
                merged[key] = [val]

        # 随机抽
        detail: Dict[str, str] = {}
        for key in self.LAYER_ORDER:
            options = merged.get(key, [])
            if options:
                detail[key] = random.choice(options)

        full = self._join(detail)

        if max_tokens and max_tokens > 0:
            full = self._truncate_to_limit(full, max_tokens, detail)

        return (full, detail) if return_detail else full

    # ---------- 内部工具 ----------

    def _join(self, detail: Dict[str, str]) -> str:
        """把各层短语按顺序拼成 prompt。"""
        parts = []
        for key in self.LAYER_ORDER:
            val = detail.get(key, "").strip()
            if val:
                parts.append(val)
        return ", ".join(parts)

    def _merge_preset(self, preset_layers: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """合并预设到默认层（预设优先）。"""
        merged: Dict[str, List[str]] = {}
        for key in self.LAYER_ORDER:
            if key in preset_layers and preset_layers[key]:
                merged[key] = list(preset_layers[key])
            else:
                merged[key] = list(self.layers.get(key, []))
        return merged

    # ---------- 预设文件加载 ----------

    def load_preset(
        self,
        preset_name: str,
        category: Optional[str] = None,
    ) -> Optional[Dict]:
        """
        加载预设文件。

        Args:
            preset_name: 预设名（不含 .py）
            category: 分类。不传时自动搜索所有分类。

        Returns:
            预设字典 或 None
        """
        candidates: List[Path] = []

        if category:
            candidates.append(PRESETS_DIR / category / f"{preset_name}.py")
        else:
            # 自动搜索所有分类目录
            if PRESETS_DIR.exists():
                for sub in sorted(PRESETS_DIR.iterdir()):
                    if sub.is_dir():
                        candidates.append(sub / f"{preset_name}.py")

        for p in candidates:
            if p.exists():
                preset = self._load_preset_file(p)
                if preset:
                    return preset

        return None

    def _load_preset_file(self, path: Path) -> Optional[Dict]:
        """从 .py 文件加载 PRESET 字典。"""
        try:
            spec = importlib.util.spec_from_file_location(
                f"preset_{path.stem}", path
            )
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            preset = getattr(mod, "PRESET", None)
            if not isinstance(preset, dict):
                print(f"   ⚠️ 预设文件缺少 PRESET 字典: {path.name}")
                return None
            return preset
        except Exception as e:
            print(f"   ⚠️ 加载预设失败 {path.name}: {e}")
            return None

    def list_presets(self) -> Dict[str, List[str]]:
        """
        列出所有预设（按分类）。

        Returns:
            {"yokai": ["tengu", "kappa", ...], "japanese": [...], ...}
        """
        result: Dict[str, List[str]] = {}
        if not PRESETS_DIR.exists():
            return result

        for sub in sorted(PRESETS_DIR.iterdir()):
            if not sub.is_dir():
                continue
            names = sorted([
                f.stem for f in sub.glob("*.py")
                if not f.stem.startswith("_") and f.stem != "__init__"
            ])
            if names:
                result[sub.name] = names

        return result

    def find_preset_by_keyword(self, text: str) -> Optional[Tuple[str, str]]:
        """
        根据用户输入的关键词，猜测想要的预设。

        Args:
            text: 用户输入

        Returns:
            (category, preset_name) 或 None
        """
        text_lower = text.lower()

        # 关键词映射：命中关键词 → 预设名
        KEYWORD_MAP = {
            # 妖怪
            "天狗": "tengu",
            "tengu": "tengu",
            "河童": "kappa",
            "kappa": "kappa",
            "九尾": "kitsune",
            "狐狸": "kitsune",
            "kitsune": "kitsune",
            "雪女": "yuki_onna",
            "yuki": "yuki_onna",
            "鬼": "oni",
            "百鬼": "hyakki_yagyo",
            "野篦坊": "noppera_bo",
            "辘轳首": "roku_ro_kubi",
            # 日本
            "浮世绘": "ukiyo_e",
            "ukiyo": "ukiyo_e",
            "日本画": "nihonga",
            "水墨": "sumi_e",
            "屏风": "byobu_e",
            "绘卷": "emaki",
            # 古风
            "工笔": "gong_bi",
            "青绿": "qing_lv",
            "白描": "bai_miao",
            "减笔": "jian_bi",
            # 源氏
            "源氏": "heian_court",
            "平安": "heian_court",
            "十二单": "junihitoe",
            "观月": "moon_viewing",
            "赏樱": "cherry_blossom",
            # 唐风
            "敦煌": "dunhuang",
            "飞天": "dunhuang",
            "唐仕女": "tang_beauty",
            "大唐": "tang_palace",
            "唐马": "tang_horse",
        }

        # 命中关键词 → 找预设
        for kw, preset_name in KEYWORD_MAP.items():
            if kw in text_lower:
                preset = self.load_preset(preset_name)
                if preset:
                    return (preset.get("category", "unknown"), preset_name)

        return None

    # ---------- 负面提示词 ----------

    @staticmethod
    def get_negative(custom: Optional[str] = None) -> str:
        """获取负面提示词（默认 + 自定义追加）。"""
        if custom:
            return f"{DEFAULT_NEGATIVE}, {custom}"
        return DEFAULT_NEGATIVE

    # ---------- 工具方法 ----------

    def get_layer_info(self) -> Dict[str, int]:
        """返回各层候选数量。"""
        return {k: len(self.layers.get(k, [])) for k in self.LAYER_ORDER}

    def get_total_combinations(self) -> int:
        """返回理论组合总数。"""
        total = 1
        for key in self.LAYER_ORDER:
            count = len(self.layers.get(key, []))
            if count == 0:
                return 0
            total *= count
        return total


# ============================================================
# 自检（直接运行本文件）
# ============================================================

if __name__ == "__main__":
    print("=" * 70)
    print("  ArtForge PromptBuilder 自检")
    print("=" * 70)

    builder = PromptBuilder()

    # 1. 各层数量
    print("\n📚 各层候选数量:")
    info = builder.get_layer_info()
    for key in builder.LAYER_ORDER:
        cn = builder.LAYER_NAMES_CN.get(key, key)
        print(f"  - {key:12s} ({cn:6s}): {info.get(key, 0):3d} 条")
    print(f"\n🎯 理论组合总数: {builder.get_total_combinations():,}")

    # 2. 随机组合
    print("\n" + "=" * 70)
    print("  【模式 1】随机组合")
    print("=" * 70)
    prompt, detail = builder.compose_random(return_detail=True)
    print(f"\n📝 Prompt:\n{prompt}\n")
    print(f"📋 明细:")
    for k, v in detail.items():
        cn = builder.LAYER_NAMES_CN.get(k, k)
        print(f"  [{cn}] {v[:60]}...")

    # 3. 索引组合（可复现）
    print("\n" + "=" * 70)
    print("  【模式 2】索引组合（index=42，可复现）")
    print("=" * 70)
    p1 = builder.compose_by_index(42)
    p2 = builder.compose_by_index(42)
    print(f"\n📝 Prompt:\n{p1}\n")
    print(f"🔁 复现验证: {'✅ 一致' if p1 == p2 else '❌ 不一致'}")

    # 4. Token 截断
    print("\n" + "=" * 70)
    print("  【模式 3】Token 截断（max_tokens=77）")
    print("=" * 70)
    prompt_full, _ = builder.compose_random(return_detail=True)
    prompt_trunc = builder.compose_random(max_tokens=77)
    print(f"\n🔍 完整长度: {builder._count_tokens(prompt_full)} tokens")
    print(f"🔍 截断长度: {builder._count_tokens(prompt_trunc)} tokens")
    print(f"\n📝 截断后 Prompt:\n{prompt_trunc}")

    # 5. 预设列表
    print("\n" + "=" * 70)
    print("  【预设列表】")
    print("=" * 70)
    presets = builder.list_presets()
    if not presets:
        print("\n⚠️ presets/ 目录为空（还没创建预设）")
        print("   → 下一步创建 presets/yokai/tengu.py")
    else:
        for cat, names in presets.items():
            print(f"\n📁 {cat} ({len(names)} 个):")
            for n in names:
                print(f"  - {n}")

    # 6. 负面提示词
    print("\n" + "=" * 70)
    print("  【负面提示词】")
    print("=" * 70)
    print(f"\n默认:\n{DEFAULT_NEGATIVE[:120]}...")

    print("\n" + "=" * 70)
    print("  ✅ 自检完成")
    print("=" * 70)