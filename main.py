# main.py
"""
ArtForge 正式入口

支持两种模式：
  1. 交互式（无参数）：逐步引导选择
  2. 快速模式（带参数）：一行命令出图

用法:
    # 交互式
    python main.py

    # 快速模式
    python main.py --preset tengu
    python main.py --preset dunhuang --category tang --engine agnes --composition horizontal
    python main.py --preset tengu --no-aging --no-inscription
    python main.py --preset feitian --category tang --language chinese --seal-scheme luxury
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

# 确保能 import 项目内模块
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from dotenv import load_dotenv
    _env = PROJECT_ROOT / ".env"
    if _env.exists():
        load_dotenv(_env)
    else:
        load_dotenv()
except ImportError:
    pass

from core.prompt_builder import PromptBuilder
from core.safety import check_safety
from api_engines import create_engine
from compose_artwork import (
    InscriptionRenderer, pick_size, theme_from_preset, load_config,
)

# ============================================================
# 个人配置（请修改为你的名字）
# ============================================================
ARTIST_NAME = "东方艺术"


# ============================================================
# 元数据
# ============================================================
CATEGORIES = {
    "japanese": " 日本文化（浮世绘/日本画/水墨/屏风/绘卷）",
    "yokai":    "👹 妖怪（天狗/河童/九尾狐/雪女/鬼）",
    "gufeng":   "🖌️ 古风绘画（水墨/工笔/青绿/减笔/白描）",
    "genji":    "📜 源氏物语（平安宫廷/十二单/屏风绘卷/观月/赏樱）",
    "tang":     "🏯 唐风（敦煌/飞天/唐仕女/宫苑/唐马）",
    "art_nude": "🎨 艺术裸体（浮世绘春画/能剧面具/花魁）",
}

ENGINES = {
    "pollinations": "✅ Pollinations（免费，无需 Key）",
    "agnes":        "✅ Agnes AI（推荐，需注册）",
    "siliconflow":  "✅ 硅基流动（免费额度）",
    "huggingface":  "✅ HuggingFace（免费限速）",
    "freeapi":      "✅ Free API（社区免费）",
}

COMPOSITIONS = {
    "vertical":   "立轴 9:16",
    "horizontal": "横卷 16:9",
    "byobu":      "屏风 4:3",
    "fan":        "团扇 1:1",
    "album":      "册页 3:4",
}

SEAL_SCHEMES = {
    "classic":  "传统经典（右下朱文方 + 左上朱文长方）",
    "contrast": "对比鲜明（右下白文方 + 左上朱文长方）",
    "luxury":   "华丽大气（右下双边框 + 左上长方 + 左下圆印）",
    "minimal":  "简洁（只有右下朱文方印）",
}

LANGUAGES = {
    "auto":     "自动（按分类判断）",
    "chinese":  "中文",
    "japanese": "日文",
}


# ============================================================
# 交互式引导
# ============================================================
def interactive_mode():
    """交互式模式"""
    print("\n" + "=" * 70)
    print("   ArtForge · 东方艺术生成工坊")
    print("=" * 70)

    builder = PromptBuilder()

    # 1. 分类
    print("\n📚 请选择主题分类：")
    cat_keys = list(CATEGORIES.keys())
    for i, k in enumerate(cat_keys, 1):
        print(f"  {i}. {CATEGORIES[k]}")
    while True:
        choice = input("\n请输入编号 [1]: ").strip() or "1"
        if choice.isdigit() and 1 <= int(choice) <= len(cat_keys):
            category = cat_keys[int(choice) - 1]
            break
        print("⚠️ 无效输入，请重新选择")

    # 2. 预设
    presets = builder.list_presets().get(category, [])
    if not presets:
        print(f"⚠️ {category} 暂无预设，回退到随机组合")
        preset = None
    else:
        print(f"\n {category} 可用预设：")
        for i, p in enumerate(presets, 1):
            print(f"  {i}. {p}")
        print(f"  0. 随机组合")
        while True:
            choice = input("\n请输入编号 [1]: ").strip() or "1"
            if choice == "0":
                preset = None
                break
            if choice.isdigit() and 1 <= int(choice) <= len(presets):
                preset = presets[int(choice) - 1]
                break
            print("⚠️ 无效输入")

    # 3. 引擎
    print("\n🔌 请选择 API 引擎：")
    eng_keys = list(ENGINES.keys())
    for i, k in enumerate(eng_keys, 1):
        print(f"  {i}. {ENGINES[k]}")
    while True:
        choice = input("\n请输入编号 [1]: ").strip() or "1"
        if choice.isdigit() and 1 <= int(choice) <= len(eng_keys):
            engine_name = eng_keys[int(choice) - 1]
            break
        print("⚠️ 无效输入")

    # 4. 画幅
    print("\n🖼️ 请选择画幅：")
    comp_keys = list(COMPOSITIONS.keys())
    for i, k in enumerate(comp_keys, 1):
        print(f"  {i}. {COMPOSITIONS[k]}")
    choice = input("\n请输入编号 [1]: ").strip() or "1"
    if choice.isdigit() and 1 <= int(choice) <= len(comp_keys):
        composition = comp_keys[int(choice) - 1]
    else:
        composition = "vertical"

    # 5. 印章方案
    print("\n🔖 请选择印章方案：")
    seal_keys = list(SEAL_SCHEMES.keys())
    for i, k in enumerate(seal_keys, 1):
        default_mark = " [默认]" if k == "contrast" else ""
        print(f"  {i}. {SEAL_SCHEMES[k]}{default_mark}")
    choice = input("\n请输入编号 [2]: ").strip() or "2"
    if choice.isdigit() and 1 <= int(choice) <= len(seal_keys):
        seal_scheme = seal_keys[int(choice) - 1]
    else:
        seal_scheme = "contrast"

    # 6. 装裱
    scroll = input("\n🎎 是否加传统装裱（绫边/轴头）？[Y/n]: ").strip().lower()
    use_scroll = scroll != "n"

    # 7. 题词
    insc = input("🖋️ 是否题词？[Y/n]: ").strip().lower()
    use_inscription = insc != "n"

    # 8. 印章
    seal = input("🔖 是否盖印？[Y/n]: ").strip().lower()
    use_seal = seal != "n"

    # 9. 水印
    wm = input("💧 是否加水印？[Y/n]: ").strip().lower()
    use_watermark = wm != "n"

    # 10. seed
    seed_str = input("\n🎲 随机种子（直接回车随机）: ").strip()
    seed = int(seed_str) if seed_str.isdigit() else None

    # 执行
    run_pipeline(
        category=category,
        preset=preset,
        engine_name=engine_name,
        composition=composition,
        use_scroll=use_scroll,
        use_aging=True,
        use_inscription=use_inscription,
        use_seal=use_seal,
        use_watermark=use_watermark,
        seal_scheme=seal_scheme,
        seed=seed,
        language="auto",
    )


# ============================================================
# 核心流水线
# ============================================================
def run_pipeline(
    category: str,
    preset: Optional[str],
    engine_name: str,
    composition: str = "vertical",
    use_scroll: bool = True,
    use_aging: bool = True,
    use_inscription: bool = True,
    use_seal: bool = True,
    use_watermark: bool = True,
    seal_scheme: str = "contrast",
    seed: Optional[int] = None,
    language: str = "auto",
    custom_prompt: Optional[str] = None,
    custom_negative: Optional[str] = None,
):
    """执行完整流水线"""
    print("\n" + "=" * 70)
    print("   开始创作")
    print("=" * 70)

    builder = PromptBuilder()

    # ---------- 1. 组 prompt ----------
    if custom_prompt:
        prompt = custom_prompt
        detail = {"subject": custom_prompt, "composition": composition}
        theme = "通用"
    elif preset:
        prompt, detail = builder.compose_preset(
            preset, category=category, return_detail=True,
        )
        theme = theme_from_preset(preset, category)
    else:
        prompt, detail = builder.compose_random(return_detail=True)
        theme = "通用"

    # 覆盖 composition 层
    comp_map = {
        "vertical":   "vertical hanging scroll, kakemono",
        "horizontal": "horizontal handscroll, emaki",
        "byobu":      "folding screen, byobu, multi-panel",
        "fan":        "round fan, circular composition",
        "album":      "square album leaf",
    }
    detail["composition"] = comp_map.get(composition, comp_map["vertical"])

    # 剔除 inscription 层（题词交 PIL 合成）
    detail.pop("inscription", None)
    parts = [detail[k] for k in builder.LAYER_ORDER if detail.get(k)]
    prompt = ", ".join(parts)

    # 负面提示词
    if custom_negative:
        negative = custom_negative
    else:
        negative = builder.get_negative()
        NO_TEXT_NEGATIVE = (
            "calligraphy, text, chinese characters, japanese text, "
            "kanji, kana, seal, stamp, signature, inscription, "
            "poem text, red seal, watermark, logo, letters, words"
        )
        negative = f"{negative}, {NO_TEXT_NEGATIVE}"

    # 安全检查
    is_safe, reason = check_safety(
        prompt, detail.get("style", ""), detail.get("subject", ""),
    )
    print(f"\n🛡️ 安全检查: {reason}")
    if not is_safe:
        print("❌ 终止生成")
        return

    # ---------- 2. 尺寸 ----------
    width, height = pick_size(detail)
    print(f"\n🖼️  画幅: {width}x{height} ({composition})")
    print(f"🎯 主题: {theme}")
    print(f"🔖 印章方案: {SEAL_SCHEMES.get(seal_scheme, seal_scheme)}")

    # ---------- 3. 出图 ----------
    config = load_config()
    engine = create_engine(engine_name, config)
    print(f"\n🎨 生成中（10-60 秒）...")
    image = engine.generate_single(
        prompt=prompt, negative=negative,
        width=width, height=height, seed=seed,
    )
    if image.mode != "RGBA":
        image = image.convert("RGBA")
    print(f"   ✅ 出图: {image.size[0]}x{image.size[1]}")

    # ---------- 4. 做旧 ----------
    if use_aging:
        try:
            from services.aging_processor import AgingProcessor
            aged = AgingProcessor(seed=seed).apply(
                image.convert("RGB"),
                texture="xuan_paper", strength=0.55,
            )
            image = aged.convert("RGBA")
            print(f"\n📜 做旧: xuan_paper")
        except Exception as e:
            print(f"\n⚠️ 做旧失败（跳过）: {e}")

    # ---------- 5. 题词 ----------
    inscription_text = ""
    if use_inscription:
        try:
            from services.inscription_generator import InscriptionGenerator
            ig = InscriptionGenerator(seed=seed)
            lang = language if language != "auto" else None
            inscription_text, meta = ig.generate(
                theme=theme, format="auto", return_meta=True,
                backend=engine_name if engine_name in
                ("agnes", "pollinations") else "auto",
                category=category,
                language=lang,
            )
            lang_cn = "中文" if meta.get("language") == "chinese" else "日文"
            print(f"\n🖋️  题词 ({lang_cn}, {meta['format_cn']}):")
            for line in inscription_text.split("\n")[:3]:
                print(f"   {line}")

            renderer = InscriptionRenderer()
            font_size = max(24, int(min(width, height) * 0.045))
            image = renderer.render(
                image, inscription_text,
                font_size=font_size,
                color=(45, 40, 35),
                position="top_right",
                margin=int(min(width, height) * 0.055),
                max_chars_per_col=8,
            )
            print(f"   ✅ 已渲染到画面右上角")
        except Exception as e:
            print(f"\n⚠️ 题词失败（跳过）: {e}")

    # ---------- 6. 印章（方案化）----------
    if use_seal:
        try:
            from services.seal_generator import SealGenerator
            sg = SealGenerator()
            image = sg.apply_scheme(
                image, ARTIST_NAME,
                scheme=seal_scheme,
                margin_ratio=0.05,
            )
            scheme_name = sg.SIGNATURE_SCHEMES[seal_scheme]["name"]
            print(f"\n🔖 印章: 「{ARTIST_NAME}」— {scheme_name}")
        except AttributeError:
            # 兼容旧版 SealGenerator
            from services.seal_generator import SealGenerator
            sg = SealGenerator()
            margin = int(min(width, height) * 0.05)
            image = sg.apply(
                image, ARTIST_NAME,
                style="bai_wen", shape="square",
                position="bottom_right",
                scale=0.14, margin=margin,
            )
            image = sg.apply(
                image, ARTIST_NAME,
                style="zhu_wen", shape="rect",
                position="top_left",
                scale=0.11, margin=margin,
            )
            print(f"\n🔖 印章: 「{ARTIST_NAME}」(旧版双印)")
        except Exception as e:
            print(f"\n⚠️ 印章失败（跳过）: {e}")

    # ---------- 7. 装裱 ----------
    if use_scroll:
        try:
            from services.scroll_composer import ScrollComposer
            sc = ScrollComposer(seed=seed)
            image = sc.compose(image.convert("RGB"), composition=composition)
            image = image.convert("RGBA")
            print(f"\n🎎 装裱: {composition}")
        except Exception as e:
            print(f"\n⚠️ 装裱失败（跳过）: {e}")

    # ---------- 8. 防伪水印 ----------
    if use_watermark:
        try:
            from services.watermark import WatermarkProcessor
            wp = WatermarkProcessor(seed=seed)
            image = wp.add_subtle_watermark(
                image,
                text=ARTIST_NAME,
                opacity=30,
                font_size=40,
                angle=-30,
                spacing_x=180,
                spacing_y=180,
            )
            if image.mode != "RGBA":
                image = image.convert("RGBA")
            print(f"\n💧 防伪水印: 「{ARTIST_NAME}」")
        except Exception as e:
            print(f"\n⚠️ 水印失败（跳过）: {e}")

    # ---------- 9. 保存 ----------
    out_dir = PROJECT_ROOT / "output" / category
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = preset or "random"
    out_path = out_dir / f"{name}_{ts}.png"
    final = image.convert("RGB")
    final.save(out_path, quality=95)

    # 元信息
    meta_path = out_path.with_suffix(".txt")
    with open(meta_path, "w", encoding="utf-8") as f:
        f.write(f"preset: {name}\n")
        f.write(f"category: {category}\n")
        f.write(f"engine: {engine_name}\n")
        f.write(f"seed: {seed}\n")
        f.write(f"size: {final.size[0]}x{final.size[1]}\n")
        f.write(f"composition: {composition}\n")
        f.write(f"scroll: {use_scroll}\n")
        f.write(f"aging: {use_aging}\n")
        f.write(f"inscription: {use_inscription}\n")
        f.write(f"seal: {use_seal} ({seal_scheme})\n")
        f.write(f"watermark: {use_watermark}\n")
        f.write(f"language: {language}\n\n")
        f.write(f"prompt:\n{prompt}\n\n")
        f.write(f"negative:\n{negative}\n")
        if inscription_text:
            f.write(f"\ninscription:\n{inscription_text}\n")

    print(f"\n✅ 成品: {out_path}")
    print(f"📝 元信息: {meta_path}")
    print("=" * 70)


# ============================================================
# CLI 入口
# ============================================================
def main():
    ap = argparse.ArgumentParser(
        description="ArtForge · 东方艺术生成工坊",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py                                                    # 交互式
  python main.py --preset tengu                                     # 快速模式
  python main.py --preset dunhuang --category tang --engine agnes
  python main.py --preset tengu --seal-scheme luxury
  python main.py --preset feitian --category tang --language chinese
  python main.py --preset tengu --no-aging --no-inscription
  python main.py --preset tengu --composition horizontal --seed 42
        """,
    )

    # 核心参数
    ap.add_argument("--preset", default=None,
                    help="预设名（如 tengu / dunhuang）")
    ap.add_argument("--category", default="yokai",
                    choices=list(CATEGORIES.keys()),
                    help="主题分类")
    ap.add_argument("--engine", default="pollinations",
                    choices=list(ENGINES.keys()),
                    help="API 引擎")
    ap.add_argument("--composition", default="vertical",
                    choices=list(COMPOSITIONS.keys()),
                    help="画幅")
    ap.add_argument("--seed", type=int, default=None,
                    help="随机种子")

    # 功能开关
    ap.add_argument("--no-scroll", action="store_true",
                    help="不加装裱")
    ap.add_argument("--no-aging", action="store_true",
                    help="不做旧")
    ap.add_argument("--no-inscription", action="store_true",
                    help="不题词")
    ap.add_argument("--no-seal", action="store_true",
                    help="不盖印")
    ap.add_argument("--no-watermark", action="store_true",
                    help="不加水印")

    # 印章方案
    ap.add_argument("--seal-scheme", default="contrast",
                    choices=list(SEAL_SCHEMES.keys()),
                    help="印章方案（默认 contrast）")

    # 题词语言
    ap.add_argument("--language", default="auto",
                    choices=list(LANGUAGES.keys()),
                    help="题词语言（默认 auto）")

    # 自定义 prompt（跳过预设）
    ap.add_argument("--prompt", default=None,
                    help="自定义 Prompt（填了就用，忽略预设）")
    ap.add_argument("--negative", default=None,
                    help="自定义负面 Prompt")

    args = ap.parse_args()

    # 判断是否走快速模式
    is_quick = any([
        args.preset,
        args.prompt,
        args.seed is not None,
        args.no_scroll,
        args.no_aging,
        args.no_inscription,
        args.no_seal,
        args.no_watermark,
        args.engine != "pollinations",
        args.composition != "vertical",
        args.seal_scheme != "contrast",
        args.language != "auto",
    ])

    if is_quick or args.preset or args.prompt:
        run_pipeline(
            category=args.category,
            preset=args.preset,
            engine_name=args.engine,
            composition=args.composition,
            use_scroll=not args.no_scroll,
            use_aging=not args.no_aging,
            use_inscription=not args.no_inscription,
            use_seal=not args.no_seal,
            use_watermark=not args.no_watermark,
            seal_scheme=args.seal_scheme,
            seed=args.seed,
            language=args.language,
            custom_prompt=args.prompt,
            custom_negative=args.negative,
        )
    else:
        interactive_mode()


if __name__ == "__main__":
    main()