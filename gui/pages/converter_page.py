# gui/pages/converter_page.py
import gradio as gr
from pathlib import Path
import sys
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


def do_convert(image: "PIL.Image", engine_name, strength, seal_text):
    try:
        from skills.ukiyoe_converter import UkiyoeConverter
        import tempfile
        conv = UkiyoeConverter({"engine": engine_name, "strength": strength})
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            image.save(f.name)
            out = conv.convert(f.name, seal_text=seal_text or None)
        if out["status"] == "success":
            from PIL import Image
            return Image.open(out["result"]["output_path"]), \
                   f"✅ 完成: {out['result']['output_path']}"
        return None, f"❌ {out.get('error')}"
    except Exception as e:
        import traceback
        return None, traceback.format_exc()


def build():
    with gr.Row():
        with gr.Column(scale=1):
            image_in = gr.Image(label="输入图片", type="pil")
            engine_name = gr.Dropdown(["pollinations", "agnes"],
                                      value="pollinations", label="引擎")
            strength = gr.Slider(0.3, 0.95, value=0.75, label="转换强度")
            seal_text = gr.Textbox("東方藝術", label="印章文字")
            btn = gr.Button("🎨 浮世绘转换", variant="primary")

        with gr.Column(scale=1):
            image_out = gr.Image(label="转换结果", type="pil")
            log_out = gr.Textbox(label="日志", lines=5)

    btn.click(do_convert, inputs=[image_in, engine_name, strength, seal_text],
              outputs=[image_out, log_out])