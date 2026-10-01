"""ArtForge GUI 启动入口 (Gradio 多选版)
用法: python run_gui_Gradio.py
"""
import sys
import socket
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

def get_lan_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

if __name__ == "__main__":
    import gradio as gr
    
    # 尝试加载预设
    presets_by_cat = {}
    try:
        from core.prompt_builder import PromptBuilder
        builder = PromptBuilder()
        presets_by_cat = builder.list_presets() or {}
    except Exception as e:
        print(f"️ 加载预设失败: {e}")

    cats = list(presets_by_cat.keys()) or ["yokai"]
    
    lan_ip = get_lan_ip()
    print()
    print("=" * 64)
    print("   ArtForge Gradio GUI (多选版)")
    print("=" * 64)
    print()
    print(f"   本机访问:   http://127.0.0.1:7860")
    print(f"   局域网访问: http://{lan_ip}:7860")
    print()
    print("=" * 64)
    print()

    # 构建支持多选的界面
    with gr.Blocks(theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 🎎 ArtForge · 东方艺术生成工坊 (支持多选)")
        
        with gr.Row():
            with gr.Column(scale=1):
                # 多选分类
                cat_dropdown = gr.Dropdown(
                    choices=cats, 
                    value=[cats[0]] if cats else [], 
                    label="主题分类 (多选)", 
                    multiselect=True
                )
                # 多选预设
                preset_dropdown = gr.Dropdown(
                    choices=[], 
                    value=[], 
                    label="预设 (多选，根据分类自动更新)", 
                    multiselect=True
                )
                engine = gr.Dropdown(choices=["pollinations", "agnes", "siliconflow"], value="pollinations", label="引擎")
                composition = gr.Radio(choices=["vertical", "horizontal", "byobu", "fan", "album"], value="vertical", label="画幅")
                seal_scheme = gr.Dropdown(choices=["classic", "contrast", "luxury", "minimal"], value="contrast", label="印章方案")
                language = gr.Dropdown(choices=["auto", "chinese", "japanese"], value="auto", label="题词语言")
                seed = gr.Number(value=-1, label="随机种子 (-1=随机)")
                
                aging = gr.Checkbox(value=True, label="做旧")
                inscription = gr.Checkbox(value=True, label="题词")
                seal = gr.Checkbox(value=True, label="印章")
                watermark = gr.Checkbox(value=True, label="水印")
                scroll = gr.Checkbox(value=True, label="装")
                
                btn = gr.Button(" 批量生成", variant="primary")
            
            with gr.Column(scale=2):
                output_img = gr.Image(label="预览 (显示最后一张)", type="filepath")
                log_box = gr.Textbox(label="执行日志", lines=10, interactive=False)

        # 联动逻辑：分类改变时更新预设列表
        def update_presets(selected_cats):
            if not selected_cats:
                return gr.update(choices=[], value=[])
            # 收集所有选中分类下的预设
            all_presets = set()
            for cat in selected_cats:
                all_presets.update(presets_by_cat.get(cat, []))
            return gr.update(choices=list(all_presets), value=list(all_presets)[:1] if all_presets else [])

        cat_dropdown.change(fn=update_presets, inputs=cat_dropdown, outputs=preset_dropdown)

        # 生成逻辑 (简化版，实际需调用你的核心模块)
        def generate(selected_cats, selected_presets, engine, composition, seal_scheme, language, seed, aging, inscription, seal, watermark, scroll):
            if not selected_cats or not selected_presets:
                return None, "⚠️ 请至少选择一个分类和一个预设！"
            
            log = f"开始批量生成\n分类: {selected_cats}\n预设: {selected_presets}\n"
            # 这里需要接入你实际的生成逻辑 (参考 Tkinter 版中的 _generate_worker)
            # 由于 Gradio 是 Web 界面，批量生成建议返回最后一张图的路径
            log += "✅ 生成逻辑待接入 (请参考 Tkinter 版的批量生成代码)\n"
            return None, log

        btn.click(fn=generate, inputs=[cat_dropdown, preset_dropdown, engine, composition, seal_scheme, language, seed, aging, inscription, seal, watermark, scroll], outputs=[output_img, log_box])

    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        inbrowser=True,
        show_error=True,
    )