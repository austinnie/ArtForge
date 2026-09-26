# gui/pages/generate_page.py
"""生图页（自动保存到 output/<category>/）"""
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

COMPOSITION_SIZES = {
    "vertical (立轴 9:16)":   (768, 1365),
    "horizontal (横卷 16:9)": (1365, 768),
    "byobu (屏风 4:3)":       (1024, 768),
    "fan (团扇 1:1)":         (1024, 1024),
    "album (册页 3:4)":       (768, 1024),
}


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


def do_generate(category, preset, engine_name, composition,
                width, height, seed, prompt_override):
    """点击【生成】按钮触发。"""
    try:
        from core.prompt_builder import PromptBuilder
        from api_engines import create_engine

        builder = PromptBuilder()
        if prompt_override and prompt_override.strip():
            prompt = prompt_override.strip()
            negative = builder.get_negative()
        else:
            if not preset:
                return None, "", "❌ 未选择预设"
            prompt, _detail = builder.compose_preset(
                preset, category=category, return_detail=True,
            )
            negative = builder.get_negative()

        engine = create_engine(engine_name, load_env_config())
        image = engine.generate_single(
            prompt=prompt,
            negative=negative,
            width=int(width),
            height=int(height),
            seed=int(seed) if seed not in (None, "") and int(seed) >= 0 else None,
        )

        # ✅ 落盘：output/<category>/<preset>_<时间戳>.png
        out_dir = ensure_dir(PROJECT_ROOT / "output" / (category or "misc"))
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = preset or "custom"
        out_path = out_dir / f"{name}_{ts}.png"
        image.save(out_path, quality=95)

        msg = (
            f"✅ 生成成功\n"
            f"📁 已保存: {out_path}\n"
            f"📐 尺寸: {image.size[0]}x{image.size[1]}"
        )
        return image, prompt, msg

    except Exception as e:
        import traceback
        return None, "", f"❌ 失败: {e}\n\n{traceback.format_exc()}"


def build():
    presets = get_preset_map()
    categories = list(presets.keys()) or ["yokai"]

    with gr.Row():
        # ---------- 左：参数 ----------
        with gr.Column(scale=1):
            gr.Markdown("### 🎨 生图参数")

            category = gr.Dropdown(
                choices=categories, value=categories[0],
                label="主题分类",
            )

            first_presets = presets.get(categories[0], [])
            preset = gr.Dropdown(
                choices=first_presets,
                value=(first_presets[0] if first_presets else None),
                label="预设",
            )

            def _on_category_change(cat):
                lst = presets.get(cat, [])
                return gr.update(choices=lst,
                                 value=(lst[0] if lst else None))
            category.change(_on_category_change, category, preset)

            engine_name = gr.Dropdown(
                choices=["pollinations", "agnes", "siliconflow"],
                value="pollinations", label="引擎",
            )

            composition = gr.Radio(
                choices=list(COMPOSITION_SIZES.keys()),
                value="vertical (立轴 9:16)",
                label="画幅",
            )

            def _on_comp_change(comp):
                w, h = COMPOSITION_SIZES.get(comp, (768, 1365))
                return gr.update(value=w), gr.update(value=h)

            with gr.Row():
                width = gr.Number(value=768, label="宽")
                height = gr.Number(value=1365, label="高")
            composition.change(_on_comp_change, composition, [width, height])

            seed = gr.Number(value=-1, label="随机种子（-1 或留空=随机）",
                             precision=0)

            prompt_override = gr.Textbox(
                label="自定义 Prompt（填了就用这个，忽略预设）",
                lines=3, placeholder="（可留空）",
            )

            with gr.Row():
                btn = gr.Button("🎨 开始生成", variant="primary", size="lg")
                open_btn = gr.Button("📂 打开输出目录")

        # ---------- 右：结果 ----------
        with gr.Column(scale=1):
            gr.Markdown("### 🖼️ 生成结果")
            image_out = gr.Image(label="图片", type="pil", height=520)
            prompt_out = gr.Textbox(label="实际使用的 Prompt", lines=4)
            status = gr.Textbox(label="状态 / 保存路径", lines=4)

    btn.click(
        do_generate,
        inputs=[category, preset, engine_name, composition,
                width, height, seed, prompt_override],
        outputs=[image_out, prompt_out, status],
    )


    # 上面 open_btn 需要 category 参数，重新绑定
    open_btn.click(
        lambda cat: _open_dir(PROJECT_ROOT / "output" / (cat or "misc")),
        inputs=[category],
        outputs=[status],
    )