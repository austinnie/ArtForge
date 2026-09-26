# gui/pages/pipeline_page.py
"""一键流水线：出图 → 做旧 → 题词 → 印章 → 水印 → 保存"""
from __future__ import annotations

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

import gradio as gr

from gui.common import (
    PROJECT_ROOT, load_env_config, get_preset_map, ensure_dir,
)

COMP_MAP = {
    "vertical (立轴 9:16)":   "vertical hanging scroll, kakemono",
    "horizontal (横卷 16:9)": "horizontal handscroll, emaki",
    "byobu (屏风 4:3)":       "folding screen, byobu, multi-panel",
    "fan (团扇 1:1)":         "round fan, circular composition",
    "album (册页 3:4)":       "square album leaf",
}

COMPOSITION_SIZE = {
    "vertical":   (768, 1365),
    "horizontal": (1365, 768),
    "byobu":      (1024, 768),
    "fan":        (1024, 1024),
    "album":      (768, 1024),
}


def _pick_size(detail):
    comp = (detail.get("composition") or "").lower()
    if any(w in comp for w in ["horizontal", "handscroll"]):
        return COMPOSITION_SIZE["horizontal"]
    if any(w in comp for w in ["fan", "round"]):
        return COMPOSITION_SIZE["fan"]
    if any(w in comp for w in ["screen", "byobu"]):
        return COMPOSITION_SIZE["byobu"]
    if any(w in comp for w in ["album"]):
        return COMPOSITION_SIZE["album"]
    return COMPOSITION_SIZE["vertical"]


def _open_dir(path) -> str:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    try:
        if sys.platform == "win32":
            os.startfile(str(p))
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(p)])
        else:
            subprocess.Popen(["xdg-open", str(p)])
        return f"📂 已打开: {p}"
    except Exception as e:
        return f"❌ 打开失败: {e}\n路径: {p}"


def run_pipeline(category, preset, engine_name, composition,
                 use_aging, use_inscription, use_seal, use_watermark, seed):
    logs = []
    try:
        from core.prompt_builder import PromptBuilder
        from api_engines import create_engine
        from compose_artwork import (
            InscriptionRenderer, theme_from_preset, ARTIST_NAME,
        )

        seed_int = None
        if seed not in (None, "", -1):
            try:
                s = int(seed)
                if s >= 0:
                    seed_int = s
            except (TypeError, ValueError):
                pass

        # ---------- 1. 组 prompt ----------
        builder = PromptBuilder()
        prompt, detail = builder.compose_preset(
            preset, category=category, return_detail=True,
        )
        theme = theme_from_preset(preset, category)

        detail["composition"] = COMP_MAP.get(
            composition, COMP_MAP["vertical (立轴 9:16)"],
        )
        detail.pop("inscription", None)
        parts = [detail[k] for k in builder.LAYER_ORDER if detail.get(k)]
        prompt = ", ".join(parts)

        negative = builder.get_negative()
        negative += (
            ", calligraphy, text, chinese characters, japanese text, "
            "kanji, kana, seal, stamp, signature, watermark, logo, "
            "letters, words, writing"
        )
        logs.append(f"✅ Prompt 就绪（主题: {theme}）")

        # ---------- 2. 出图 ----------
        width, height = _pick_size(detail)
        engine = create_engine(engine_name, load_env_config())
        image = engine.generate_single(
            prompt=prompt, negative=negative,
            width=width, height=height, seed=seed_int,
        )
        if image.mode != "RGBA":
            image = image.convert("RGBA")
        logs.append(f"✅ 出图 {image.size[0]}x{image.size[1]}")

        # ---------- 3. 做旧 ----------
        if use_aging:
            try:
                from services.aging_processor import AgingProcessor
                aged = AgingProcessor(seed=seed_int).apply(
                    image.convert("RGB"),
                    texture="xuan_paper", strength=0.55,
                )
                image = aged.convert("RGBA")
                logs.append("✅ 做旧（宣纸纹理）")
            except Exception as e:
                logs.append(f"⚠️ 做旧失败（跳过）: {e}")

        # ---------- 4. 题词 ----------
        inscription_text = ""
        if use_inscription:
            try:
                from services.inscription_generator import InscriptionGenerator
                ig = InscriptionGenerator(seed=seed_int)
                inscription_text, meta = ig.generate(
                    theme=theme, format="auto", return_meta=True,
                    backend=engine_name if engine_name in
                    ("agnes", "pollinations") else "auto",
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
                logs.append(f"✅ 题词: {inscription_text[:40]}")
            except Exception as e:
                logs.append(f"⚠️ 题词失败（跳过）: {e}")

        # ---------- 5. 印章 ----------
        if use_seal:
            try:
                from services.seal_generator import SealGenerator
                sg = SealGenerator()
                margin = int(min(width, height) * 0.05)
                image = sg.apply(
                    image, ARTIST_NAME,
                    style="zhu_wen", shape="square",
                    position="bottom_right",
                    scale=0.14, margin=margin,
                )
                image = sg.apply(
                    image, ARTIST_NAME,
                    style="zhu_wen", shape="rect",
                    position="top_left",
                    scale=0.11, margin=margin,
                )
                logs.append(f"✅ 印章「{ARTIST_NAME}」")
            except Exception as e:
                logs.append(f"⚠️ 印章失败（跳过）: {e}")

        # ---------- 6. 防伪水印（纯中文）----------
        if use_watermark:
            try:
                from services.watermark import WatermarkProcessor
                wp = WatermarkProcessor(seed=seed_int)
                watermark_text = ARTIST_NAME
                image = wp.add_subtle_watermark(
                    image,
                    text=watermark_text,
                    opacity=30,
                    font_size=40,
                    angle=-30,
                    spacing_x=180,
                    spacing_y=180,
                )
                if image.mode != "RGBA":
                    image = image.convert("RGBA")
                logs.append(f"✅ 防伪水印: {watermark_text}")
            except Exception as e:
                logs.append(f"⚠️ 水印失败（跳过）: {e}")

        # ---------- 7. 保存 ----------
        out_dir = ensure_dir(PROJECT_ROOT / "output" / (category or "misc"))
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = out_dir / f"{preset}_{ts}.png"
        image.convert("RGB").save(out_path, quality=95)
        logs.append(f"✅ 保存: {out_path}")

        return image.convert("RGB"), "\n".join(logs), str(out_path)

    except Exception as e:
        import traceback
        logs.append(f"\n❌ 失败: {e}")
        logs.append(traceback.format_exc())
        return None, "\n".join(logs), ""


def build():
    presets = get_preset_map()
    categories = list(presets.keys()) or ["yokai"]

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 🚀 一键生成完整作品")

            category = gr.Dropdown(
                choices=categories, value=categories[0], label="主题分类",
            )
            first_presets = presets.get(categories[0], [])
            preset = gr.Dropdown(
                choices=first_presets,
                value=(first_presets[0] if first_presets else None),
                label="预设",
            )

            def _on_cat(cat):
                lst = presets.get(cat, [])
                return gr.update(choices=lst,
                                 value=(lst[0] if lst else None))
            category.change(_on_cat, category, preset)

            engine_name = gr.Dropdown(
                choices=["pollinations", "agnes", "siliconflow"],
                value="pollinations", label="引擎",
            )
            composition = gr.Radio(
                choices=list(COMP_MAP.keys()),
                value="vertical (立轴 9:16)", label="画幅",
            )
            with gr.Row():
                use_aging = gr.Checkbox(True, label="做旧")
                use_inscription = gr.Checkbox(True, label="题词")
                use_seal = gr.Checkbox(True, label="印章")
                use_watermark = gr.Checkbox(True, label="水印")

            seed = gr.Number(value=-1,
                             label="随机种子（-1 或留空=随机）",
                             precision=0)

            with gr.Row():
                btn = gr.Button("🚀 一键生成", variant="primary", size="lg")
                open_btn = gr.Button("📂 打开输出目录")

        with gr.Column(scale=1):
            gr.Markdown("### 🖼️ 成品预览")
            image_out = gr.Image(label="成品", type="pil", height=520)
            log_out = gr.Textbox(label="执行日志", lines=14)
            path_out = gr.Textbox(label="输出路径")

    btn.click(
        run_pipeline,
        inputs=[category, preset, engine_name, composition,
                use_aging, use_inscription, use_seal, use_watermark, seed],
        outputs=[image_out, log_out, path_out],
    )

    open_btn.click(
        lambda cat: _open_dir(PROJECT_ROOT / "output" / (cat or "misc")),
        inputs=[category],
        outputs=[log_out],
    )