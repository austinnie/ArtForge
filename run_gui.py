# run_gui.py
"""ArtForge GUI 启动入口
用法: python run_gui.py
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

# run_gui.py
if __name__ == "__main__":
    from gui.app import build_ui
    build_ui().launch(
        server_name="127.0.0.1",
        server_port=7860,
        inbrowser=True,
        show_error=True,
        theme=__import__("gradio").themes.Soft(),   # ← 加这行
    )