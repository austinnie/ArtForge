# music_generator

自适应音乐生成 Skill。根据情绪和风格，自动生成 MIDI 编曲并合成为 MP3，可选生成歌词。

## 主要特性

- **双引擎**：
  - **MIDI 引擎**：`midiutil` 编曲 → `fluidsynth` + SoundFont 渲染 → `ffmpeg` 合成 MP3
  - **MusicGen 引擎**：Meta MusicGen 模型，端到端生成音频
- **5 种情绪**：宁静 / 深情 / 欢乐 / 壮丽 / 神秘
- **10+ 编曲风格**：交响乐、弦乐四重奏、铜管、爵士、摇滚、中国风等
- **多乐器轨道**：钢琴、弦乐、木管、铜管等
- **歌词生成**（可选）：Ollama 本地大模型生成，或使用默认模板
- **自动回退**：MusicGen 不可用时自动回退到 MIDI 引擎

## 安装

### Python 依赖

```bash
pip install midiutil
# MusicGen 引擎需要：
pip install audiocraft  # 或 torch + transformers
```

### 外部工具

| 工具 | 用途 | 安装 |
|------|------|------|
| FFmpeg | MIDI → MP3 合成 | https://ffmpeg.org/ |
| FluidSynth | MIDI → WAV 渲染 | https://www.fluidsynth.org/ |
| SoundFont | 乐器音色库 | 将 `.sf2` 放到项目根目录 ⚠️ |

> SoundFont 文件较大（`SGM-V2.01.sf2` 约 200MB+），已在 `.gitignore` 中排除，需自行下载。

## 快速使用

### CLI

```bash
# 基础生成（默认：MIDI 引擎，宁静情绪）
python skills/music_generator/music_generator_cli.py --emotion 宁静

# 指定风格 + 情绪 + 时长
python skills/music_generator/music_generator_cli.py \
  --emotion 壮丽 \
  --style "交响乐" \
  --duration 60 \
  --output output/music/

# 生成歌词 + 音乐
python skills/music_generator/music_generator_cli.py \
  --emotion 深情 \
  --lyrics \
  --model ollama

# 交响乐生成器（更复杂的多轨道）
python skills/music_generator/generate_symphony.py \
  --style "弦乐四重奏" \
  --emotion "宁静"
```

⚠️ 参数名以实际 CLI 为准，请核对 `music_generator_cli.py` 的 `argparse` 定义。

### 作为 Skill 调用

```python
from skills.music_generator import MusicGenerator

gen = MusicGenerator({
    "output_dir": "./output/music",
    "engine": "midi",           # midi / musicgen
    "ai_model": "qwen2.5",      # 用于歌词生成
    "ollama_url": "http://localhost:11434",
})

result = gen.execute(
    emotion="宁静",
    style="钢琴独奏",
    duration=60,
    with_lyrics=True,
)

if result["status"] == "success":
    print(result["result"]["audio_file"])
    print(result["result"]["lyrics"])
```

## 情绪与风格

### 情绪（5 种）⚠️ 以代码为准

| 情绪 | 特点 |
|------|------|
| 宁静 | 舒缓、慢节奏、大调 |
| 深情 | 抒情、中速、弦乐为主 |
| 欢乐 | 明快、跳跃、大调 |
| 壮丽 | 宏大、交响、铜管 |
| 神秘 | 小调、悬疑、氛围 |

### 编曲风格（10+ 种）⚠️ 以代码为准

交响乐、弦乐四重奏、钢琴独奏、铜管重奏、爵士、摇滚、中国风、电子、环境、民谣……

## 输出

每次生成会在 `output_dir` 下创建一个带时间戳的目录：

```
output/music/20260914_153022_宁静_钢琴独奏/
├── music.mid          # MIDI 源文件
├── music.mp3          # 最终 MP3
├── lyrics.txt         # 歌词（如启用）
└── metadata.json      # 情绪、风格、时长、种子等
```

⚠️ 目录结构以实际代码为准。

## 依赖检查

`music_generator` 在启动时会检查：

- `midiutil` Python 包
- `fluidsynth` 可执行文件是否在 PATH
- SoundFont 文件是否存在
- `ffmpeg` 是否可用
- （如用 MusicGen）`torch` / `audiocraft` 是否安装

任一缺失会抛出异常，便于上层（如 `multimedia/workflow.py`）捕获并回退到其它引擎。

## 与其它 Skill 组合

`music_generator` 被 `multimedia/workflow.py` 调用，用于多媒体成片流程：

```
小说生成 → 场景拆分 → 视频生成 → TTS 配音 → 🎵 音乐生成 → 字幕 → 合成
```

在 `MultimediaWorkflow` 中，`_generate_music` 会：

1. 优先调用 `music_generator` 生成 MP3
2. 失败时回退到 `MusicMaestro` + `fluidsynth` 的 MIDI 模式
3. 都失败时继续后续合成，不中断整体流程

## 常见问题

**Q: 生成时提示找不到 fluidsynth？**
A: 确认 `fluidsynth` 已安装且可执行文件在 PATH 中。Windows 下可从 https://github.com/FluidSynth/fluidsynth/releases 下载。

**Q: SoundFont 文件放哪里？**
A: 默认在项目根目录查找 `*.sf2`。可在 `.env` 中通过 `SOUNDFONT_PATH` 指定 ⚠️。

**Q: MusicGen 引擎很慢 / 显存不足？**
A: 会在检测失败时自动回退到 MIDI 引擎。也可显式指定 `engine="midi"`。

**Q: 生成的音乐很短？**
A: 默认时长可能较短，用 `--duration 60` 指定秒数。

## 相关文件

```
skills/music_generator/
├── skill.py                    # MusicGenerator 主类
├── music_generator_cli.py      # CLI 入口（MIDI → MP3）
└── generate_symphony.py        # 交响乐生成器（多轨道）
```