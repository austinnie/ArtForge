# server/run_server.py
"""
一键启动 ArtForge PWA 服务

用法:
    python server/run_server.py
    python server/run_server.py --port 8080
    python server/run_server.py --host 0.0.0.0 --port 8000
"""

import argparse
import socket
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def get_lan_ip() -> str:
    """获取本机局域网 IP，用于手机访问"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--reload", action="store_true", help="开发模式自动重载")
    args = ap.parse_args()

    lan_ip = get_lan_ip()

    print()
    print("=" * 64)
    print("   🎎 ArtForge PWA 服务")
    print("=" * 64)
    print()
    print(f"   本机访问:   http://127.0.0.1:{args.port}")
    print(f"   局域网访问: http://{lan_ip}:{args.port}")
    print()
    print("   📱 手机浏览器打开上面的『局域网访问』地址")
    print("      然后菜单 → 『添加到主屏幕』即可当 App 用")
    print()
    print("   ⚠️ 手机必须和电脑在同一个 WiFi 下")
    print()
    print("=" * 64)
    print()

    import uvicorn
    uvicorn.run(
        "pwa.api:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info",
    )


if __name__ == "__main__":
    main()