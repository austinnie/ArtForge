# main.py
"""
ArtForge 正式入口
支持两种模式：
1. 交互式（无参数）：逐步引导选择
2. 快速模式（带参数）：一行命令出图

用法:
  python main.py                                    # 交互式
  python main.py --preset tengu                     # 快速模式
  python main.py --preset dunhuang --engine agnes --scroll
  python main.py --preset tengu --no-aging --no-inscription
  python main.py --preset feitian --category tang --language chinese  # 强制中文
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
ARTIST_NAME = "东方艺术"  # ✅ 改成你的名字，如 "李太白"、"Zhang San"

# ============================================================
# 主题/预设/引擎 元数据
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


# ============================================================
# 交互式引导
# ============================================================
def interactive_mode():
    """交互式模式"""
    print("\n" + "=" * 70)
    print("   ArtForge · 东方艺术生成工坊")
    print("=" * 70)

    builder = PromptBuilder()

    # 1. 选主题
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

    # 2. 选预设
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

    # 3. 选引擎
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
    print("\n🖼️ 请选择画幅（直接回车默认立轴）：")
    print("  1. 立轴 (9:16)  2. 横卷 (16:9)  3. 屏风 (4:3)")
    print("  4. 团扇 (1:1)   5. 册页 (3:4)")
    comp_map = {"1": "vertical", "2": "horizontal", "3": "byobu",
                "4": "fan", "5": "album"}
    choice = input("\n请输入编号 [1]: ").strip() or "1"
    composition = comp_map.get(choice, "vertical")

    # 5. 装
    scroll = input("\n🎎 是否加传统装裱（绫边/轴头）？[Y/n]: ").strip().lower()
    use_scroll = scroll != "n"

    # 6. seed
    seed_str = input("\n🎲 随机种子（直接回车随机）: ").strip()
    seed = int(seed_str) if seed_str.isdigit() else None

    # 执行
    run_pipeline(
        category=category,
        preset=preset,
        engine_name=engine_name,
        composition=composition,
        use_scroll=use_scroll,
        seed=seed,
        language="auto",  # ✅ 新增：交互式默认自动检测
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
    seed: Optional[int] = None,
    no_aging: bool = False,
    no_inscription: bool = False,
    no_seal: bool = False,
    language: str = "auto",  # ✅ 新增：题词语言参数
):
    """执行完整流水线"""
    print("\n" + "=" * 70)
    print("   开始创作")
    print("=" * 70)

    builder = PromptBuilder()

    # 1. 组 prompt
    if preset:
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
    # 重新拼装 prompt
    parts = [detail[k] for k in builder.LAYER_ORDER if detail.get(k)]
    prompt = ", ".join(parts)

    # 剔除 inscription 层（让 PIL 合成）
    if "inscription" in detail:
        detail.pop("inscription")
        parts = [detail[k] for k in builder.LAYER_ORDER if detail.get(k)]
        prompt = ", ".join(parts)

    negative = builder.get_negative()
    NO_TEXT_NEGATIVE = (
        "calligraphy, text, chinese characters, japanese text, "
        "kanji, kana, seal, stamp, signature, inscription, "
        "poem text, red seal, watermark, logo, letters, words"
    )
    negative = f"{negative}, {NO_TEXT_NEGATIVE}"

    # 安全检查
    is_safe, reason = check_safety(prompt, detail.get("style", ""), detail.get("subject", ""))
    print(f"\n🛡️ 安全检查: {reason}")
    if not is_safe:
        print("❌ 终止生成")
        return

    # 2. 尺寸
    width, height = pick_size(detail)
    print(f"\n🖼️  画幅: {width}x{height} ({composition})")
    print(f" 主题: {theme}")

    # 3. 出图
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

    # 4. 做旧
    if not no_aging:
        from services.aging_processor import AgingProcessor
        aged = AgingProcessor(seed=seed).apply(image.convert("RGB"), texture="xuan_paper", strength=0.55)
        image = aged.convert("RGBA")
        print(f"\n📜 做旧: xuan_paper")

    # 5. 题词
    inscription_text = ""
    if not no_inscription:
        from services.inscription_generator import InscriptionGenerator
        ig = InscriptionGenerator(seed=seed)
        
        # ✅ 传递 language 参数（auto 时传 None，让 generator 自动检测）
        lang = language if language != "auto" else None
        
        inscription_text, meta = ig.generate(
            theme=theme, format="auto", return_meta=True,
            backend=engine_name if engine_name in ("agnes", "pollinations") else "auto",
            category=category,  # ✅ 新增：传递分类，用于自动检测语言
            language=lang,      # ✅ 新增：传递强制语言
        )
        
        # ✅ 打印时显示语言
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

    # 6. 印章
    if not no_seal:
        from services.seal_generator import SealGenerator
        sg = SealGenerator()
        margin = int(min(width, height) * 0.05)
        image = sg.apply(image, ARTIST_NAME, style="zhu_wen", shape="square",
                         position="bottom_right", scale=0.14, margin=margin)
        image = sg.apply(image, ARTIST_NAME, style="zhu_wen", shape="rect",
                         position="top_left", scale=0.11, margin=margin)
        print(f"\n🔖 印章: 右下「{ARTIST_NAME}」+ 左上「{ARTIST_NAME}」")


    # 7. 装裱
    if use_scroll:
        from services.scroll_composer import ScrollComposer
        sc = ScrollComposer(seed=seed)
        image = sc.compose(image.convert("RGB"), composition=composition)
        image = image.convert("RGBA")
        print(f"\n🎎 装裱: {composition}")

    # 7.5 防伪水印（极低透明度，不易察觉）
    from services.watermark import WatermarkProcessor
    wp = WatermarkProcessor(seed=seed)
    # 使用艺人名字 + 项目名作为水印内容
    watermark_text = f"{ARTIST_NAME} · ArtForge"
    image = wp.add_subtle_watermark(
        image, 
        text=watermark_text, 
        opacity=10,          # ✅ 极低透明度（正常几乎不可见）
        font_size=36,        # 字号
        angle=-25,           # 倾斜角度
        spacing_x=180,       # 水平间距
        spacing_y=180,       # 垂直间距
    )
    print(f"\n🛡️  防伪水印: 已嵌入「{watermark_text}」(opacity=10)")


    # 8. 保存
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
        f.write(f"preset: {name}\ncategory: {category}\nengine: {engine_name}\n")
        f.write(f"seed: {seed}\nsize: {final.size[0]}x{final.size[1]}\n")
        f.write(f"composition: {composition}\nscroll: {use_scroll}\n")
        f.write(f"language: {language}\n\n")  # ✅ 新增：记录语言
        f.write(f"prompt:\n{prompt}\n\nnegative:\n{negative}\n")
        if inscription_text:
            f.write(f"\ninscription:\n{inscription_text}\n")

    print(f"\n✅ 成品: {out_path}")
    print(f"📝 元信息: {meta_path}")
    print("=" * 70)
    
    # 9. 生成社交媒体文案 (可选)
    if args.format_wechat:  # 需要在 argparse 里加 --format-wechat
        from skills.wechat_formatter.formatter import WechatFormatter
        wf = WechatFormatter(out_path, meta_path, inscription_text)
        wf.generate_markdown(out_path.with_suffix(".md"))
        print(f"\n📱 微信/知乎文案: {out_path.with_suffix('.md')}")    


# ============================================================
# CLI 入口
# ============================================================
def main():
    ap = argparse.ArgumentParser(description="ArtForge · 东方艺术生成工坊")
    ap.add_argument("--preset", default=None, help="预设名（如 tengu / dunhuang）")
    ap.add_argument("--category", default="yokai", choices=list(CATEGORIES.keys()))
    ap.add_argument("--engine", default="pollinations", choices=list(ENGINES.keys()))
    ap.add_argument("--composition", default="vertical",
                    choices=["vertical", "horizontal", "byobu", "fan", "album"])
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--no-scroll", action="store_true", help="不加装裱")
    ap.add_argument("--no-aging", action="store_true")
    ap.add_argument("--no-inscription", action="store_true")
    ap.add_argument("--no-seal", action="store_true")
    ap.add_argument("--language", default="auto",
                    choices=["auto", "chinese", "japanese"],
                    help="题词语言（auto=按分类自动，chinese=中文，japanese=日文）")  # ✅ 新增
    args = ap.parse_args()

    # 有任何参数 → 快速模式；否则 → 交互式
    is_quick = any([args.preset, args.seed is not None,
                    args.no_scroll, args.no_aging, args.no_inscription, args.no_seal,
                    args.engine != "pollinations", args.composition != "vertical"])

    if is_quick or args.preset:
        run_pipeline(
            category=args.category,
            preset=args.preset,
            engine_name=args.engine,
            composition=args.composition,
            use_scroll=not args.no_scroll,
            seed=args.seed,
            no_aging=args.no_aging,
            no_inscription=args.no_inscription,
            no_seal=args.no_seal,
            language=args.language,  # ✅ 新增：传递语言参数
        )
    else:
        interactive_mode()


if __name__ == "__main__":
    main()