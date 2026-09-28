# scripts/convert_bgm.py
"""
将 assets/bgm 下的 MIDI 文件转换为 MP3 并重命名
利用项目自带的 FluidSynth 和 SoundFont
"""
import os
import subprocess
import re
import random
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BGM_DIR = PROJECT_ROOT / "assets" / "bgm"

# 你项目里的 FluidSynth 和音色库路径
FLUIDSYNTH_EXE = PROJECT_ROOT / "skills" / "music_generator" / "soundfonts" / "fluidsynth-v2.6.0-win10-x64-cpp11" / "bin" / "fluidsynth.exe"
SOUNDFONT = PROJECT_ROOT / "skills" / "music_generator" / "soundfonts" / "SGM-V2.01.sf2"
# 如果上面那个不存在，试下面这个
if not SOUNDFONT.exists():
    SOUNDFONT = PROJECT_ROOT / "skills" / "music_generator" / "soundfonts" / "GeneralUser-GS.sf2"

def get_emotion(filename):
    """从文件名提取情绪 (peaceful, epic, etc.)"""
    name = filename.lower()
    if "epic" in name: return "epic"
    if "melancholic" in name: return "sad"
    if "joyful" in name: return "happy"
    if "mysterious" in name: return "mystery"
    return "peaceful" # 默认

def main():
    if not BGM_DIR.exists():
        print(f"❌ 目录不存在: {BGM_DIR}")
        return
    
    if not FLUIDSYNTH_EXE.exists():
        print(f" 找不到 FluidSynth: {FLUIDSYNTH_EXE}")
        print("请先运行 music_generator 技能或手动下载 fluidsynth")
        return

    mid_files = list(BGM_DIR.glob("*.mid"))
    if not mid_files:
        print("✅ 没有 MIDI 文件需要转换")
        return

    print(f"🔄 发现 {len(mid_files)} 个 MIDI 文件，开始转换...")
    
    # 按情绪分组计数，用于生成序号
    counters = {"epic": 1, "sad": 1, "happy": 1, "mystery": 1, "peaceful": 1}
    
    for mid_file in mid_files:
        emotion = get_emotion(mid_file.name)
        idx = counters[emotion]
        counters[emotion] += 1
        
        # 目标文件名：01_peaceful.mp3
        new_name = f"{idx:02d}_{emotion}.mp3"
        out_mp3 = BGM_DIR / new_name
        
        # 如果已经转过了，跳过
        if out_mp3.exists():
            print(f"️  跳过 (已存在): {new_name}")
            continue
            
        temp_wav = BGM_DIR / "temp_convert.wav"
        
        print(f"🎵 转换: {mid_file.name} -> {new_name}")
        
        try:
            # 1. FluidSynth: MIDI -> WAV
            # -ni: 非交互模式, -F: 输出文件, -r: 采样率
            cmd_fluid = [
                str(FLUIDSYNTH_EXE), "-ni",
                "-F", str(temp_wav),
                "-r", "44100",
                str(SOUNDFONT),
                str(mid_file)
            ]
            subprocess.run(cmd_fluid, capture_output=True, check=True)
            
            # 2. FFmpeg: WAV -> MP3
            cmd_ffmpeg = [
                "ffmpeg", "-y",
                "-i", str(temp_wav),
                "-b:a", "192k",
                str(out_mp3)
            ]
            subprocess.run(cmd_ffmpeg, capture_output=True, check=True)
            
            print(f"   ✅ 成功")
            
        except Exception as e:
            print(f"   ❌ 失败: {e}")
        finally:
            if temp_wav.exists():
                temp_wav.unlink()

    print("\n🎉 转换完成！现在 assets/bgm 下应该有 MP3 文件了。")

if __name__ == "__main__":
    main()