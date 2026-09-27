# run_gui.py
"""ArtForge GUI 启动入口
用法: python run_gui.py
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))


def get_lan_ip() -> str:
    import socket
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
    from gui.app import build_ui

    lan_ip = get_lan_ip()

    print()
    print("=" * 64)
    print("   ArtForge Gradio GUI")
    print("=" * 64)
    print()
    print(f"   本机访问:   http://127.0.0.1:7860")
    print(f"   局域网访问: http://{lan_ip}:7860")
    print()
    print("   手机浏览器打开『局域网访问』地址即可")
    print("   (手机必须和电脑在同一 WiFi)")
    print()
    print("=" * 64)
    print()

    build_ui().launch(
        server_name="0.0.0.0",     # ← 关键：允许局域网访问
        server_port=7860,
        inbrowser=True,
        show_error=True,
        theme=gr.themes.Soft(),
    )