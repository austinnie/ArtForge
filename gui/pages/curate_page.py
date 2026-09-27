# gui/pages/curate_page.py
import gradio as gr
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


def do_curate(image_dir, title, theme,
              gen_docx, gen_pdf, gen_clipboard,
              do_format, do_publish):
    logs = []
    fmt = None           # 提前声明，避免"推送"分支 NameError
    article_dir = None

    try:
        if not Path(image_dir).exists():
            return "❌ 目录不存在", "", None

        # ---------- 1. 鉴赏 ----------
        from skills.image_curator import ImageCurator
        curator = ImageCurator({
            "generate_html": True,
            "generate_docx": gen_docx,            # ✅ 从复选框读
            "generate_pdf": gen_pdf,              # ✅ 从复选框读
            "generate_clipboard": gen_clipboard,  # ✅ 从复选框读
        })
        r = curator.curate(image_dir, title=title or None)
        if r["status"] != "success":
            return f"❌ 鉴赏失败: {r.get('error')}", "", None

        res = r["result"]
        md_path = res["article_path"]
        logs.append(f"✅ 鉴赏完成: {md_path}")

        # 把生成的文件路径全部打进日志，方便你看
        if res.get("html_path"):
            logs.append(f"   🌐 HTML: {res['html_path']}")
        if res.get("docx_path"):
            logs.append(f"   📘 Word: {res['docx_path']}")
        if res.get("pdf_path"):
            logs.append(f"   📄 PDF:  {res['pdf_path']}")
        if res.get("clipboard_path"):
            logs.append(f"   📋 富文本: {res['clipboard_path']}")

        # ---------- 2. 排版 ----------
        if do_format:
            from skills.wechat_formatter import WechatFormatter
            fmt = WechatFormatter()
            fr = fmt.format(md_path, theme=theme, open=False)
            if fr["status"] != "success":
                return ("\n".join(logs)
                        + f"\n❌ 排版失败: {fr.get('error')}",
                        md_path, None)
            article_dir = fr["result"]["article_dir"]
            logs.append(f"✅ 排版完成: {article_dir}")
        else:
            article_dir = None

        # ---------- 3. 推送 ----------
        if do_publish and article_dir and fmt:
            pub = fmt.publish(article_dir)
            if pub["status"] == "success":
                logs.append("✅ 已推送公众号草稿箱")
            else:
                logs.append(f"❌ 推送失败: {pub.get('error')}")

        return "\n".join(logs), md_path, article_dir

    except Exception:
        import traceback
        return traceback.format_exc(), "", None


def build():
    with gr.Row():
        with gr.Column(scale=1):
            image_dir = gr.Textbox(
                label="图片目录", placeholder="output/yokai")
            title = gr.Textbox(label="文章标题（可留空）")
            theme = gr.Dropdown(
                ["newspaper", "terracotta", "bytedance", "chinese",
                 "github", "magazine", "warm-card", "ocean-card"],
                value="newspaper", label="排版主题",
            )

            # ✅ 新增：输出格式开关
            gr.Markdown("**输出格式**")
            with gr.Row():
                gen_docx = gr.Checkbox(True, label="Word (.docx)")
                gen_pdf = gr.Checkbox(True, label="PDF")
            gen_clipboard = gr.Checkbox(True, label="富文本 (微信/知乎可粘贴)")

            # 排版/推送开关
            gr.Markdown("**后续操作**")
            with gr.Row():
                do_format = gr.Checkbox(True, label="排版")
                do_publish = gr.Checkbox(False, label="推送草稿箱")

            btn = gr.Button("🔍 开始鉴赏", variant="primary")

        with gr.Column(scale=1):
            log_out = gr.Textbox(label="执行日志", lines=18)
            md_out = gr.Textbox(label="Markdown 路径")
            dir_out = gr.Textbox(label="排版输出目录")

    btn.click(
        do_curate,
        inputs=[
            image_dir, title, theme,
            gen_docx, gen_pdf, gen_clipboard,
            do_format, do_publish,
        ],
        outputs=[log_out, md_out, dir_out],
    )