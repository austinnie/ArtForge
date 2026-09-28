#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
为无声视频添加背景音乐
用法:
  python scripts/add_music.py                          # 自动处理 output/videos 下所有视频，随机配乐
  python scripts/add_music.py --video path/to/video.mp4 --music path/to/music.mp3
"""
import argparse
import subprocess
import shutil
import random
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VIDEO_DIR = PROJECT_ROOT / "output" / "videos"
MUSIC_DIR = PROJECT_ROOT / "assets" / "music"
OUT_DIR = VIDEO_DIR / "mixed"  # 处理后的视频放在这里

def get_random_music():
    if not MUSIC_DIR.exists():
        return None
    mp3s = list(MUSIC_DIR.glob("*.mp3"))
    if not mp3s:
        return None
    return random.choice(mp3s)

def add_music(video_path: Path, music_path: Path, output_path: Path):
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        print("❌ 未找到 ffmpeg")
        return False

    print(f"🎬 视频: {video_path.name}")
    print(f"🎵 音乐: {music_path.name}")
    
    # FFmpeg 命令：音乐循环 (-stream_loop -1)，以视频长度为准 (-shortest)
    cmd = [
        ffmpeg, "-y",
        "-i", str(video_path),
        "-stream_loop", "-1", "-i", str(music_path),
        "-shortest",
        "-c:v", "copy",       # 视频流不重编码，速度极快
        "-c:a", "aac", "-b:a", "128k",
        str(output_path)
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, check=True)
        print(f"✅ 成功: {output_path.name}\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 失败: {e.stderr.decode()}\n")
        return False

def main():
    parser = argparse.ArgumentParser(description="为视频添加背景音乐")
    parser.add_argument("--video", type=str, help="指定单个视频文件路径")
    parser.add_argument("--music", type=str, help="指定音乐文件路径 (不指定则随机)")
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if args.video:
        video_files = [Path(args.video)]
    else:
        video_files = list(VIDEO_DIR.glob("*.mp4"))

    if not video_files:
        print("❌ 未找到视频文件")
        return

    print(f"🔍 找到 {len(video_files)} 个视频待处理\n")

    success_count = 0
    for v_file in video_files:
        if args.music:
            m_file = Path(args.music)
        else:
            m_file = get_random_music()
            
        if not m_file or not m_file.exists():
            print(f"⚠️ 未找到音乐文件，跳过 {v_file.name}")
            continue

        out_file = OUT_DIR / f"music_{v_file.name}"
        
        if add_music(v_file, m_file, out_file):
            success_count += 1

    print(f"🎉 完成: {success_count}/{len(video_files)} 个视频已添加音乐")
    print(f" 输出目录: {OUT_DIR}")

if __name__ == "__main__":
    main()