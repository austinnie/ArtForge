# gui/pages/pipeline_page.py
import gradio as gr
from pathlib import Path
import sys, shutil
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from core.prompt_builder import PromptBuilder
from api_engines import create_engine
from compose_artwork import (
    InscriptionRenderer, pick_size, theme_from_preset, load_config, ARTIST_NAME,
)

def _open_dir(path: Path) -> str:
    """跨平台打开目录"""
    path.mkdir(parents=True, exist_ok=True)
    try:
        if sys.platform == "win32":
            os.startfile(str(path))
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])
        return f"📂 已打开: {path}"
    except Exception as e:
        return f"❌ 打开失败: {e}\n路径: {path}"


def run_pipeline(category, preset, engine_name, composition,
                 use_aging, use_inscription, use_seal, seed):
    try:
        logs = []
        builder = PromptBuilder()
        prompt, detail = builder.compose_preset(
            preset, category=category, return_detail=True,
        )
        theme = theme_from_preset(preset, category)

        # 覆盖画幅
        comp_map = {
            "vertical":   "vertical hanging scroll, kakemono",
            "horizontal": "horizontal handscroll, emaki",
            "byobu":      "folding screen, byobu, multi-panel",
            "fan":        "round fan, circular composition",
            "album":      "square album leaf",
        }
        detail["composition"] = comp_map.get(composition, comp_map["vertical"])
        parts = [detail[k] for k in builder.LAYER_ORDER if detail.get(k)]
        prompt = ", ".join(parts)

        # 剔除 inscription 层
        detail.pop("inscription", None)
        parts = [detail[k] for k in builder.LAYER_ORDER if detail.get(k)]
        prompt = ", ".join(parts)

        negative = builder.get_negative()
        negative += (", calligraphy, text, chinese characters, japanese text, "
                     "kanji, kana, seal, stamp, signature, watermark, logo, letters, words")
        logs.append(f"✅ Prompt 就绪 (主题: {theme})")

        # 出图
        width, height = pick_size(detail)
        engine = create_engine(engine_name, load_config())
        image = engine.generate_single(
            prompt=prompt, negative=negative,
            width=width, height=height,
            seed=int(seed) if seed else None,
        )
        if image.mode != "RGBA":
            image = image.convert("RGBA")
        logs.append(f"✅ 出图 {image.size[0]}x{image.size[1]}")

        # 做旧
        if use_aging:
            from services.aging_processor import AgingProcessor
            aged = AgingProcessor(seed=int(seed) if seed else None).apply(
                image.convert("RGB"), texture="xuan_paper", strength=0.55,
            )
            image = aged.convert("RGBA")
            logs.append("✅ 做旧完成")

        # 题词
        inscription_text = ""
        if use_inscription:
            from services.inscription_generator import InscriptionGenerator
            ig = InscriptionGenerator(seed=int(seed) if seed else None)
            inscription_text, meta = ig.generate(
                theme=theme, format="auto", return_meta=True,
                backend=engine_name if engine_name in ("agnes", "pollinations") else "auto",
                category=category,
            )
            renderer = InscriptionRenderer()
            font_size = max(24, int(min(width, height) * 0.045))
            image = renderer.render(
                image, inscription_text, font_size=font_size,
                color=(45, 40, 35), position="top_right",
                margin=int(min(width, height) * 0.055),
                max_chars_per_col=8,
            )
            logs.append(f"✅ 题词: {inscription_text[:30]}...")

        # 印章
        if use_seal:
            from services.seal_generator import SealGenerator
            sg = SealGenerator()
            margin = int(min(width, height) * 0.05)
            image = sg.apply(image, ARTIST_NAME, style="zhu_wen", shape="square",
                             position="bottom_right", scale=0.14, margin=margin)
            image = sg.apply(image, ARTIST_NAME, style="zhu_wen", shape="rect",
                             position="top_left", scale=0.11, margin=margin)
            logs.append(f"✅ 印章「{ARTIST_NAME}」")

        # 保存
        from datetime import datetime
        out_dir = PROJECT_ROOT / "output" / category
        out_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = out_dir / f"{preset}_{ts}.png"
        image.convert("RGB").save(out_path, quality=95)
        logs.append(f"✅ 保存: {out_path}")

        return image, "\n".join(logs), str(out_path)
    except Exception as e:
        import traceback
        return None, traceback.format_exc(), ""


def build():
    builder = PromptBuilder()
    presets = builder.list_presets()
    categories = list(presets.keys()) or ["yokai"]

    with gr.Row():
        with gr.Column(scale=1):
            category = gr.Dropdown(categories, value=categories[0], label="主题分类")
            preset = gr.Dropdown(
                presets.get(categories[0], []),
                value=(presets.get(categories[0]) or [""])[0],
                label="预设",
            )
            def update_presets(cat):
                lst = presets.get(cat, [])
                return gr.update(choices=lst, value=(lst[0] if lst else None))
            category.change(update_presets, category, preset)

            engine_name = gr.Dropdown(
                ["pollinations", "agnes", "siliconflow"],
                value="pollinations", label="引擎",
            )
            composition = gr.Radio(
                ["vertical", "horizontal", "byobu", "fan", "album"],
                value="vertical", label="画幅",
            )
            with gr.Row():
                use_aging = gr.Checkbox(True, label="做旧")
                use_inscription = gr.Checkbox(True, label="题词")
                use_seal = gr.Checkbox(True, label="印章")
            seed = gr.Number(label="随机种子", precision=0)
            with gr.Row():
                btn = gr.Button("🚀 一键生成完整作品", variant="primary", size="lg")
                open_btn = gr.Button("📂 打开输出目录")

        with gr.Column(scale=1):
            image_out = gr.Image(label="成品预览", type="pil")
            log_out = gr.Textbox(label="执行日志", lines=15)
            path_out = gr.Textbox(label="输出路径")

    btn.click(
        run_pipeline,
        inputs=[category, preset, engine_name, composition,
                use_aging, use_inscription, use_seal, seed],
        outputs=[image_out, log_out, path_out],
    )
    open_btn.click(
        lambda cat: _open_dir(PROJECT_ROOT / "output" / (cat or "misc")),
        inputs=[category],
        outputs=[log_out],
    )    