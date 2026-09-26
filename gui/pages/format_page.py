# gui/pages/format_page.py
import gradio as gr
from pathlib import Path
import sys
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


def do_format(md_path, theme, gallery, do_cover, do_publish):
    logs = []
    try:
        if not Path(md_path).exists():
            return "❌ 文件不存在", None
        from skills.wechat_formatter import WechatFormatter
        fmt = WechatFormatter()
        r = fmt.format(md_path, theme=theme, gallery=gallery, open=False)
        if r["status"] != "success":
            return f"❌ 排版失败: {r.get('error')}", None
        data = r["result"]
        logs.append(f"✅ 排版完成: {data.get('article_dir')}")

        cover_path = None
        if do_cover and data.get("title"):
            cr = fmt.generate_cover(data["title"], data["title"])
            if cr["status"] == "success":
                cover_path = cr["result"]["cover_path"]
                logs.append(f"✅ 封面: {cover_path}")

        if do_publish and data.get("article_dir"):
            pr = fmt.publish(data["article_dir"], cover_path)
            if pr["status"] == "success":
                logs.append("✅ 已推送")
            else:
                logs.append(f"❌ 推送失败: {pr.get('error')}")

        return "\n".join(logs), data.get("preview_path")
    except Exception as e:
        import traceback
        return traceback.format_exc(), None


def build():
    with gr.Row():
        with gr.Column(scale=1):
            md_path = gr.Textbox(label="Markdown 路径")
            theme = gr.Dropdown(
                ["newspaper", "terracotta", "bytedance", "chinese",
                 "github", "magazine", "warm-card", "ocean-card",
                 "midnight", "bauhaus", "sports"],
                value="newspaper", label="主题",
            )
            with gr.Row():
                gallery = gr.Checkbox(False, label="主题画廊")
                do_cover = gr.Checkbox(False, label="生成封面")
                do_publish = gr.Checkbox(False, label="推送草稿箱")
            btn = gr.Button("📰 排版", variant="primary")

        with gr.Column(scale=1):
            log_out = gr.Textbox(label="执行日志", lines=12)
            preview = gr.Textbox(label="预览 HTML 路径")

    btn.click(do_format, inputs=[md_path, theme, gallery, do_cover, do_publish],
              outputs=[log_out, preview])