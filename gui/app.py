# gui/app.py
"""ArtForge GUI 主入口"""
import gradio as gr
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from gui.pages import (
    generate_page,
    curate_page,
    format_page,
    pipeline_page,
    settings_page,
    converter_page,
)

def build_ui():
    with gr.Blocks(title="ArtForge · 东方艺术生成工坊") as demo:
        gr.Markdown("# 🎎 ArtForge · 东方艺术生成工坊")

        with gr.Tabs():
            with gr.Tab("🎨 生图"):
                generate_page.build()
            with gr.Tab("🖼️ 鉴赏"):
                curate_page.build()
            with gr.Tab("📰 排版推送"):
                format_page.build()
            with gr.Tab("🚀 一键流水线"):
                pipeline_page.build()
            with gr.Tab("🎨 浮世绘转换"):
                converter_page.build()
            with gr.Tab("⚙️ 配置"):
                settings_page.build()

    return demo

if __name__ == "__main__":
    build_ui().launch(server_name="127.0.0.1", server_port=7860, inbrowser=True)