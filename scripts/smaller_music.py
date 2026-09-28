#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量优化音乐文件：
1. 转换为 128kbps MP3（减小文件大小）
2. 截取前 60 秒（适合视频背景音乐）
3. 输出到 assets/bgm 目录
"""
import subprocess
import sys
from pathlib import Path
import shutil

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MUSIC_DIR = PROJECT_ROOT / "assets" / "music"
BGM_DIR = PROJECT_ROOT / "assets" / "bgm"

def optimize_music(input_file: Path, output_file: Path, duration: int = 60):
    """
    优化音乐文件
    :param input_file: 输入文件
    :param output_file: 输出文件
    :param duration: 截取时长（秒）
    """
    if not shutil.which("ffmpeg"):
        print("❌ 未找到 ffmpeg，请先安装")
        return False
    
    try:
        # 获取原文件时长
        cmd_probe = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(input_file)
        ]
        result = subprocess.run(cmd_probe, capture_output=True, text=True)
        original_duration = float(result.stdout.strip())
        
        # 决定实际截取时长（不超过原文件时长）
        actual_duration = min(duration, original_duration)
        
        print(f"🎵 处理: {input_file.name}")
        print(f"   原时长: {original_duration:.1f}s, 截取: {actual_duration:.1f}s")
        
        # FFmpeg 转换命令：
        # -t: 截取时长
        # -b:a 128k: 比特率 128kbps
        # -ac 2: 立体声
        # -ar 44100: 采样率 44.1kHz
        cmd = [
            "ffmpeg", "-y",
            "-i", str(input_file),
            "-t", str(actual_duration),
            "-b:a", "128k",
            "-ac", "2",
            "-ar", "44100",
            "-vn",  # 不要视频
            str(output_file)
        ]
        
        subprocess.run(cmd, capture_output=True, check=True)
        
        # 显示文件大小
        size_kb = output_file.stat().st_size / 1024
        print(f"   ✅ 完成: {output_file.name} ({size_kb:.0f} KB)")
        return True
        
    except Exception as e:
        print(f"   ❌ 失败: {e}")
        return False

def main():
    if not MUSIC_DIR.exists():
        print(f"❌ 音乐目录不存在: {MUSIC_DIR}")
        return
    
    # 创建 bgm 目录
    BGM_DIR.mkdir(parents=True, exist_ok=True)
    
    mp3_files = list(MUSIC_DIR.glob("*.mp3"))
    if not mp3_files:
        print(f" {MUSIC_DIR} 下没有 MP3 文件")
        return
    
    print(f" 发现 {len(mp3_files)} 个 MP3 文件")
    print(f" 输出目录: {BGM_DIR}")
    print(f"⏱️  截取时长: 60 秒")
    print("=" * 60)
    
    success_count = 0
    for i, mp3_file in enumerate(mp3_files, 1):
        print(f"\n[{i}/{len(mp3_files)}]")
        
        # 输出文件名：optimized_原文件名.mp3
        output_name = f"optimized_{mp3_file.stem}.mp3"
        output_file = BGM_DIR / output_name
        
        if optimize_music(mp3_file, output_file):
            success_count += 1
    
    print("\n" + "=" * 60)
    print(f"✅ 完成: {success_count}/{len(mp3_files)} 个文件处理成功")
    print(f"📂 优化后的文件在: {BGM_DIR}")
    
    # 复制第一个文件作为 default.mp3
    if success_count > 0:
        optimized_files = list(BGM_DIR.glob("optimized_*.mp3"))
        if optimized_files:
            default_file = BGM_DIR / "default.mp3"
            shutil.copy2(optimized_files[0], default_file)
            print(f"🎯 已设置默认背景音乐: {default_file.name}")

if __name__ == "__main__":
    main()