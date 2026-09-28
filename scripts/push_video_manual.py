#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
手动推送视频到视频号 (自动处理登录)
用法:
  python scripts/push_video_manual.py --video path/to/video.mp4 --title "我的视频"
"""
import argparse
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SAU_CLI = PROJECT_ROOT / "skills" / "social_auto_upload" / "sau_cli.py"
PYTHON_EXE = sys.executable

def run_cmd(cmd_list, description):
    print(f"▶ {description}...")
    try:
        result = subprocess.run(cmd_list, cwd=str(PROJECT_ROOT))
        if result.returncode == 0:
            print(f"✅ {description} 成功\n")
            return True
        else:
            print(f"❌ {description} 失败\n")
            return False
    except Exception as e:
        print(f"💥 异常: {e}\n")
        return False

def main():
    parser = argparse.ArgumentParser(description="手动推送视频到视频号")
    parser.add_argument("--video", type=str, required=True, help="视频文件路径")
    parser.add_argument("--title", type=str, required=True, help="视频标题")
    parser.add_argument("--cover", type=str, help="封面图路径 (可选)")
    parser.add_argument("--account", type=str, default="test", help="账号名 (默认 test)")
    args = parser.parse_args()

    video_path = Path(args.video).resolve()
    if not video_path.exists():
        print(f"❌ 视频文件不存在: {video_path}")
        return

    cover_path = Path(args.cover).resolve() if args.cover else None

    print("=" * 60)
    print("  🚀 视频号推送助手")
    print("=" * 60)
    
    # 1. 登录
    login_cmd = [
        PYTHON_EXE, str(SAU_CLI),
        "tencent", "login",
        "--account", args.account,
        "--headed"  # 弹出浏览器扫码
    ]
    
    print("步骤 1: 登录视频号")
    print("💡 请在弹出的浏览器中扫码登录，登录成功后脚本会自动继续...")
    if not run_cmd(login_cmd, "登录"):
        print("❌ 登录失败，无法继续推送")
        return

    # 2. 推送
    push_cmd = [
        PYTHON_EXE, str(SAU_CLI),
        "tencent", "upload-video",
        "--account", args.account,
        "--file", str(video_path),
        "--title", args.title,
        "--headed"
    ]
    
    if cover_path:
        push_cmd.extend(["--thumbnail", str(cover_path)])

    print("步骤 2: 推送视频")
    run_cmd(push_cmd, "推送视频")

if __name__ == "__main__":
    main()