# gui/pages/settings_page.py
import gradio as gr
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def load_env():
    env_file = PROJECT_ROOT / ".env"
    if not env_file.exists():
        return "（.env 不存在，请复制 .env.sample）"
    return env_file.read_text(encoding="utf-8")


def save_env(content):
    env_file = PROJECT_ROOT / ".env"
    env_file.write_text(content, encoding="utf-8")
    return "✅ 已保存"


def build():
    with gr.Column():
        gr.Markdown("### ⚙️ 环境变量配置（.env）")
        env_text = gr.Textbox(
            value=load_env(), lines=20, label=".env 内容",
            placeholder="POLLINATIONS_API_KEY=...\nAGNES_API_KEY=...",
        )
        with gr.Row():
            reload_btn = gr.Button("🔄 重新加载")
            save_btn = gr.Button("💾 保存", variant="primary")
        status = gr.Textbox(label="状态")

        reload_btn.click(lambda: load_env(), outputs=env_text)
        save_btn.click(save_env, inputs=env_text, outputs=status)

