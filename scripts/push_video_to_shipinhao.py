#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
视频号手动推送助手 (增强版)
功能：
1. 自动扫描 output/daily 目录，找到最新的视频文件。
2. 支持手动指定视频路径和标题。
3. 分离登录和上传步骤，避免重复扫码。
用法:
python scripts/push_video_manual.py                        # 自动找最新视频并推送
python scripts/push_video_manual.py --video path/to.mp4    # 指定视频
python scripts/push_video_manual.py --login-only           # 仅登录（更新 Cookie）
"""
import argparse
import subprocess
import sys
import glob
import os
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SAU_CLI = PROJECT_ROOT / "skills" / "social_auto_upload" / "sau_cli.py"
PYTHON_EXE = sys.executable
OUTPUT_DIR = PROJECT_ROOT / "output" / "daily"

def run_cmd(cmd_list, description):
    """执行命令并打印结果"""
    print(f"\n▶ {description}...")
    print(f"  命令: {' '.join(cmd_list)}")
    try:
        # 使用 subprocess.run 并实时打印输出
        process = subprocess.Popen(
            cmd_list, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True, 
            encoding='utf-8',
            errors='replace'
        )
        for line in process.stdout:
            print(line, end='')
        process.wait()
        
        if process.returncode == 0:
            print(f"\n✅ {description} 成功")
            return True
        else:
            print(f"\n❌ {description} 失败 (返回码: {process.returncode})")
            return False
    except Exception as e:
        print(f"\n 异常: {e}")
        return False

def find_latest_video():
    """自动寻找 output/daily 目录下最新的 mp4 文件"""
    if not OUTPUT_DIR.exists():
        return None
    
    # 查找所有 mp4 文件
    video_files = glob.glob(str(OUTPUT_DIR / "**" / "*.mp4"), recursive=True)
    if not video_files:
        return None
    
    # 按修改时间排序，返回最新的
    video_files.sort(key=os.path.getmtime, reverse=True)
    return video_files[0]

def main():
    parser = argparse.ArgumentParser(description="视频号手动推送助手")
    parser.add_argument("--video", type=str, help="视频文件路径 (不填则自动找最新视频)")
    parser.add_argument("--title", type=str, help="视频标题 (不填则手动输入)")
    parser.add_argument("--cover", type=str, help="封面图路径 (可选)")
    parser.add_argument("--account", type=str, default="test", help="账号名 (默认 test)")
    parser.add_argument("--login-only", action="store_true", help="仅执行登录，不上传")
    
    args = parser.parse_args()

    print("=" * 60)
    print("  🚀 视频号手动推送助手 (增强版)")
    print("=" * 60)

    # 1. 登录步骤
    print("\n【步骤 1】登录视频号")
    print("💡 请在弹出的浏览器中扫码登录。登录成功后 Cookie 会保存一段时间。")
    login_cmd = [
        PYTHON_EXE, str(SAU_CLI),
        "tencent", "login",
        "--account", args.account,
        "--headed"
    ]
    if not run_cmd(login_cmd, "登录视频号"):
        print("❌ 登录失败，无法继续。")
        return

    if args.login_only:
        print("\n✅ 仅登录模式，任务结束。")
        return

    # 2. 确定视频路径
    video_path = args.video
    if not video_path:
        print("\n【步骤 2】寻找视频文件")
        video_path = find_latest_video()
        if not video_path:
            print(f"❌ 在 {OUTPUT_DIR} 下没有找到任何 mp4 视频文件。")
            print("   请使用 --video 参数指定路径。")
            return
        print(f"🔍 自动找到最新视频: {video_path}")
    else:
        video_path = Path(video_path).resolve()
        if not video_path.exists():
            print(f"❌ 视频文件不存在: {video_path}")
            return

    # 3. 确定标题
    title = args.title
    if not title:
        print("\n【步骤 3】输入视频标题")
        # 默认标题使用文件名或当前日期
        default_title = video_path.stem
        title = input(f"请输入标题 (回车使用默认: {default_title}): ").strip()
        if not title:
            title = default_title

    # 4. 推送视频
    print(f"\n【步骤 4】推送视频")
    print(f"   视频: {video_path}")
    print(f"   标题: {title}")
    
    push_cmd = [
        PYTHON_EXE, str(SAU_CLI),
        "tencent", "upload-video",
        "--account", args.account,
        "--file", str(video_path),
        "--title", title,
        "--headed"
    ]
    
    if args.cover:
        cover_path = Path(args.cover).resolve()
        if cover_path.exists():
            push_cmd.extend(["--thumbnail", str(cover_path)])
            print(f"   封面: {cover_path}")
        else:
            print(f"⚠️ 封面文件不存在，将使用默认封面: {cover_path}")

    run_cmd(push_cmd, "上传视频到视频号")
    
    print("\n" + "=" * 60)
    print("  🎉 推送流程结束")
    print("=" * 60)

if __name__ == "__main__":
    main()