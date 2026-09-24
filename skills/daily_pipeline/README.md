# daily_task.py · PromptForge 每日自动化任务

一键完成：**生成图片 → AI 鉴赏写文章 → 追加二维码 → 微信排版 → 推送草稿箱**

---

## 参数一览

| 参数 | 短写 | 取值 | 默认 | 说明 |
|---|---|---|---|---|
| `--topic` | `-t` | 任意字符串 | 随机 | 主题。给了就按主题猜风格，自动匹配预设 |
| `--preset` | `-p` | 预设名 | 随机 | 预设。给了就按预设分类，自动匹配主题 |
| `--preset-category` | — | `机甲` / `国风` / `人像` / `动漫` / `素描` / `动物` / `设计` / `风景` | 无 | 限定预设分类，主题也从对应风格里抽 |
| `--vary-preset` | — | 开关 | 关 | 每张图从同分类随机换一个预设，风格更散 |
| `--count` | `-c` | 1~N | `6` | 生成张数 |
| `--theme` | — | 任意排版主题名 | `newspaper` | 微信排版主题（见 `skills/wechat_formatter/themes/`） |
| `--output-root` | — | 路径 | `output/daily` | 生图输出根目录 |
| `--qr` | — | 路径 | `assets/qr/公众号结束处.png` | 文末二维码 |
| `--no-publish` | — | 开关 | 关（**默认推送**） | 只生成本地文件，不推草稿箱 |
| `--open` | — | 开关 | 关 | 完成后打开浏览器预览 |
| `--skip-curate` | — | 开关 | 关 | 只生图，跳过鉴赏/写文章/排版 |
| `--skip-generate` | — | 开关 | 关 | 跳过生图，用 `--image-dir` 里的现成图片 |
| `--image-dir` | — | 路径 | 无 | 配合 `--skip-generate` |
| `--list-presets` | — | 开关 | — | 列出所有预设（按分类）后退出 |
| `--list-topics` | — | 开关 | — | 列出所有主题（按风格）后退出 |

> ⚠️ **没有 `--publish`**。默认就是推送，要关掉用 `--no-publish`。
> ⚠️ **没有 `--topics-file`**。自定义主题走根目录的 `topics.txt` 自动加载。

---

## 用法示例

**方式一：命令行（脚本）**

# CLI（脚本）
python scripts/daily_task.py --count 2 --no-publish --open

# Skill CLI
python -m skills.daily_pipeline.skill --count 2 --no-publish --open

**方式二：Python API（Skill）**

# Python API
python -c "from skills.daily_pipeline import DailyPipeline; r=DailyPipeline().execute(count=1, skip_curate=True); print(r['result']['image_dir'])"


# 代码
```python
from skills.daily_pipeline import DailyPipeline

pipe = DailyPipeline()
result = pipe.execute(
    topic="月下松林",
    count=6,
    theme="terracotta",
    publish=True,
)
print(result["result"]["preview_path"])
```

## 参数用法重点说明

### 一、日常使用（最常用）

```bash
# 全随机：主题+预设智能匹配，6 张图，推草稿箱
python scripts/daily_task.py

# 全随机 + 每张图换预设（风格更多样）
python scripts/daily_task.py --vary-preset

# 全随机 + 8 张图
python scripts/daily_task.py --count 8

# 全随机 + 打开浏览器看效果 + 不推送
python scripts/daily_task.py --no-publish --open
```

### 二、指定主题 / 预设

```bash
# 只给主题 → 自动猜风格 → 从对应分类的预设里随机
python scripts/daily_task.py --topic "月下松林"

# 只给预设 → 自动查分类 → 从对应风格的主题里随机
python scripts/daily_task.py --preset mecha_dark_queen

# 两个都给 → 精确锁定
python scripts/daily_task.py --topic "机械蝴蝶" --preset mecha_glow

# 限定预设分类（主题也从对应风格里抽）
python scripts/daily_task.py --preset-category 国风
python scripts/daily_task.py --preset-category 机甲 --count 8
python scripts/daily_task.py --preset-category 风景 --vary-preset
```

### 三、排版 / 推送控制

```bash
# 换排版主题
python scripts/daily_task.py --theme terracotta

# 不推送，只看本地结果
python scripts/daily_task.py --no-publish

# 不推送 + 打开浏览器
python scripts/daily_task.py --no-publish --open

# 换文末二维码
python scripts/daily_task.py --qr "assets/qr/我的二维码.png"
```

### 四、跳过某些步骤

```bash
# 只生图，不写文章不排版（快速出图）
python scripts/daily_task.py --count 10 --skip-curate

# 只策展已有图片（不调 API 生图）
python scripts/daily_task.py --skip-generate --image-dir "output/daily/20260917_072939_images"

# 只策展 + 不推送
python scripts/daily_task.py --skip-generate --image-dir "output/daily/xxx" --no-publish
```

### 五、查看清单

```bash
# 列出所有预设（按分类，共 100+ 个）
python scripts/daily_task.py --list-presets

# 列出所有主题（按风格，共 115 个）
python scripts/daily_task.py --list-topics

# 查看排版主题（33 个）
dir skills\wechat_formatter\themes\*.json /b
```

### 六、CI / 计划任务里用

```bash
# 计划任务：全随机 + 换预设 + 推草稿箱 + 不弹浏览器
python scripts/daily_task.py --count 6 --theme newspaper --vary-preset

# GitHub Actions：必须加 --no-publish（出口 IP 不在白名单）
python scripts/daily_task.py --count 6 --vary-preset --no-publish
```

---

## 常见组合速查

| 目标 | 命令 |
|---|---|
| 随便看看效果 | `python scripts/daily_task.py --count 2 --no-publish --open` |
| 正式每日任务 | `python scripts/daily_task.py --count 6 --vary-preset` |
| 调试某预设 | `python scripts/daily_task.py --preset chinese_ink --count 4 --no-publish --open` |
| 调试某主题 | `python scripts/daily_task.py --topic "雪豹特写" --count 4 --no-publish --open` |
| 只出图 | `python scripts/daily_task.py --count 10 --skip-curate` |
| 复用已有图 | `python scripts/daily_task.py --skip-generate --image-dir output/daily/xxx` |

---

## 智能匹配规则

| 你给的参数 | 系统行为 |
|---|---|
| 都没给 | 随机分类 → 从该分类的预设 + 对应风格主题各抽一个 |
| 只给 `--topic` | 猜风格 → 从对应分类的预设里随机 |
| 只给 `--preset` | 查分类 → 从对应风格的主题里随机 |
| `--preset-category` | 从该分类预设里抽 + 对应风格主题里抽 |
| `--topic` + `--preset` 都给 | 不做匹配，直接用 |

**风格 ↔ 分类 映射表**：

| 风格 | 可用预设分类 |
|---|---|
| `mecha` | 机甲 |
| `chinese` | 国风 |
| `portrait` | 人像 / 素描 |
| `anime` | 动漫 |
| `animal` | 动物 / 素描 |
| `design` | 设计 |
| `landscape` | 风景 |

---

## 图片多样化机制

脚本内置两层多样化，保证 6 张图看起来不雷同：

### 1. 变体模板（默认开启）

16 个变体，每张图用不同的构图 / 视角 / 氛围：

```
{topic}, wide cinematic establishing shot, epic scale
{topic}, close-up detail shot, shallow depth of field
{topic}, low angle dramatic perspective, imposing presence
{topic}, aerial bird's-eye view, sweeping panorama
{topic}, symmetrical centered composition, elegant balance
{topic}, dynamic diagonal composition, sense of motion
{topic}, golden hour warm tones, romantic atmosphere
{topic}, blue hour cool tones, moody cinematic lighting
{topic}, minimalist composition, generous negative space
{topic}, rule of thirds framing, natural candid feel
{topic}, three-quarter view, soft diffused studio lighting
{topic}, striking silhouette against bright backdrop
{topic}, macro detail focus, extremely fine texture
{topic}, environmental portrait, subject in context
{topic}, back view, mysterious and contemplative
{topic}, top-down flat lay composition, artistic arrangement
```

每天运行时会**随机打乱**这 16 个模板，取前 N 个。

### 2. `--vary-preset`（可选）

开启后，**第一张用原预设**（保持风格锚点），**从第二张开始**从同分类随机换预设。

比如原预设是 `mecha_glow`，则会从"机甲"分类的其他预设里随机：
`mecha_dark_queen` / `mecha_girl_doll_kit` / `mecha_winged_overlord` / ...

---

## 自定义主题池

在 `scripts/topics.txt` 放自定义主题（跟 `daily_task.py` 同目录），每行一个，`#` 开头为注释。
自定义主题的**权重是内置主题的 3 倍**，想让某主题更高频可以重复几行。

**格式示例**：

```
# 自定义主题池（每行一个）
东京雨夜
机械折扇
未来禅意庭院
青花瓷机甲
赛博竹林
```

**生效方式**：需在 `daily_task.py` 里加 3 处代码支持（见下方"扩展代码"）。

---

## 输出目录结构

```
output/
├── daily/
│   ├── 20260917_074031_images/          # 当日生成的图片
│   │   ├── 作品01.png                    # 已重命名，去掉 AI 痕迹
│   │   ├── 作品02.png
│   │   └── ...
│   └── logs/
│       └── run_20260917.log             # run_daily.bat 的日志
│
├── articles/
│   └── 20260917_074045_主题 2026-09-17/ # image_curator 产物
│       ├── article.md
│       ├── article.html
│       ├── article.docx
│       ├── article.pdf
│       ├── clipboard.html
│       ├── metadata.json
│       └── assets/
│
└── wechat/
    └── 20260917_074100_article/         # wechat_formatter 产物
        ├── article.html                 # 微信兼容 HTML
        ├── preview.html                 # 浏览器预览
        └── images/                      # 含文末二维码
```

---

## 本地调度

### `scripts/run_daily.bat`

```bat
@echo off
chcp 65001 >nul
cd /d "%~dp0\.."

set LOG_DIR=output\daily\logs
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
set LOG_FILE=%LOG_DIR%\run_%date:~0,4%%date:~5,2%%date:~8,2%.log

echo [%date% %time%] === PromptForge 每日任务开始 === >> "%LOG_FILE%"

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

python scripts\daily_task.py --count 6 --theme newspaper --vary-preset >> "%LOG_FILE%" 2>&1

set EXIT_CODE=%ERRORLEVEL%
echo [%date% %time%] === 任务结束，退出码 %EXIT_CODE% === >> "%LOG_FILE%"

if not %EXIT_CODE%==0 (
    echo ⚠️ PromptForge 每日任务失败，请查看 %LOG_FILE%
)

exit /b %EXIT_CODE%
```

### `scripts/register_task.ps1`

以管理员身份运行一次，注册"每天 08:00"的计划任务：

```powershell
$TaskName   = "PromptForge_Daily"
$ProjectDir = "E:\SD_OpenVINO\PromptForge"
$BatPath    = Join-Path $ProjectDir "scripts\run_daily.bat"

Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

$Trigger = New-ScheduledTaskTrigger -Daily -At "08:00"
$Action  = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$BatPath`"" -WorkingDirectory $ProjectDir
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1)

Register-ScheduledTask `
    -TaskName $TaskName `
    -Trigger $Trigger `
    -Action $Action `
    -Settings $Settings `
    -Description "PromptForge 每日生图 + 鉴赏 + 排版" `
    -Force

Write-Host "✅ 计划任务已注册：$TaskName" -ForegroundColor Green
```

**验证**：

```powershell
Get-ScheduledTask -TaskName PromptForge_Daily | Format-List
Start-ScheduledTask -TaskName PromptForge_Daily   # 立即测试
```

---

## GitHub Actions

`.github/workflows/daily-task.yml` 参考（注意 **CI 里必须加 `--no-publish`**）：

```yaml
name: Daily PromptForge

on:
  schedule:
    - cron: "0 22 * * *"   # UTC 22:00 = 北京时间 06:00
  workflow_dispatch:

jobs:
  daily:
    runs-on: ubuntu-latest
    timeout-minutes: 60

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.10"
          cache: pip

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install requests Pillow python-dotenv python-docx markdown

      - name: Run daily task
        env:
          AGNES_API_KEY:      ${{ secrets.AGNES_API_KEY }}
          AGNES_BASE_URL:     ${{ secrets.AGNES_BASE_URL }}
          AGNES_IMAGE_MODEL:  ${{ secrets.AGNES_IMAGE_MODEL }}
          AGNES_TEXT_MODEL:   ${{ secrets.AGNES_TEXT_MODEL }}
          AGNES_VIDEO_MODEL:  ${{ secrets.AGNES_VIDEO_MODEL }}
          AGNES_VISION_MODEL: ${{ secrets.AGNES_VISION_MODEL }}
          LLM_ENABLED: "false"
        run: |
          python scripts/daily_task.py \
            --count 6 --vary-preset --no-publish

      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: daily-output-${{ github.run_number }}
          path: |
            output/daily/
            output/wechat/
          retention-days: 30
```

**必需的 Secrets**（仓库 → Settings → Secrets and variables → Actions）：

| Secret | 说明 | 必填 |
|---|---|---|
| `AGNES_API_KEY` | Agnes AI 密钥（生图 + 鉴赏） | ✅ |
| `AGNES_BASE_URL` | `https://apihub.agnes-ai.com/v1` | ✅ |
| `AGNES_IMAGE_MODEL` | `agnes-image-2.1-flash` | ⭕ |
| `AGNES_TEXT_MODEL` | `agnes-2.5-flash` | ⭕ |
| `AGNES_VISION_MODEL` | `agnes-2.5-flash` | ⭕ |

> ⚠️ **CI 里千万别推公众号**。GitHub Actions 出口 IP 不固定，微信 API 要求 IP 白名单，100% 失败。用 `--no-publish` 只产 artifact，你下载后本地跑一次 `--publish` 推送即可。

---

## 常见问题

### Q1：`ValueError: relative paths can't be expressed as file URIs`

早期版本 bug，已在最新代码修复（所有路径都 `.resolve()`）。升级到最新版 `daily_task.py`。

### Q2：图片都很像

1. 确认**没有**加 `--topic` 和 `--preset`（两个都给会锁死主题）
2. 加 `--vary-preset` 让每张图换预设
3. 已经默认开启"变体模板"，如果还觉得像，说明预设本身可选空间太小，换一个预设池更大的分类

### Q3：文章里图片标题是 `074031 text2img xxx`

说明 `skills/image_curator/writers.py` 的 `make_heading()` 没更新。按最新代码替换即可（识别"作品01"格式）。

### Q4：文件名还是 `20260917_074031_text2img_未来都市夜景_ethereal_beautifu.png`

说明 `skills/image_generator/skill.py` 的 `_save_image()` 没更新，或者 `daily_task.py` 的重命名段没生效。检查两处都按最新版替换。

### Q5：推送失败 `errcode=40164`

IP 不在白名单。查当前公网 IP：

```cmd
curl ifconfig.me
```

加到微信后台 → 基础信息 → API IP 白名单。家宽 IP 会变，变了要重新加。

### Q6：推送失败 `errcode=48001`

未认证的个人订阅号无草稿箱 API 权限。只能手动浏览器打开 `preview.html` → 复制粘贴。

### Q7：`--list-presets` 看不到排版主题

排版主题（33 个）在 `skills/wechat_formatter/themes/`，跟 `--list-presets`（风格预设，100+ 个）不是一回事。

```bash
dir skills\wechat_formatter\themes\*.json /b
```

---

## 扩展：自定义主题池

### 代码改动（3 处）

**① `daily_task.py` 顶部加**：

```python
TOPICS_FILE = PROJECT_ROOT / scripts/ "topics.txt"


def load_custom_topics() -> list[str]:
    """读取 topics.txt（每行一个主题，# 注释）。不存在或为空就返回 []。"""
    if not TOPICS_FILE.exists():
        return []
    lines = TOPICS_FILE.read_text(encoding="utf-8").splitlines()
    return [l.strip() for l in lines if l.strip() and not l.strip().startswith("#")]
```

**② `_pick_from_styles()` 里混入自定义主题**：

```python
def _pick_from_styles(styles: list[str]) -> str:
    pool: list[str] = []
    for s in styles:
        pool.extend(TOPICS_BY_STYLE.get(s, []))
    if not pool:
        pool = ALL_TOPICS
    # 混入自定义主题
    pool.extend(load_custom_topics())
    return random.choice(pool)
```

**③ `topics.txt` 格式**：

```
# 自定义主题池（每行一个，# 开头为注释）
东京雨夜
机械折扇
未来禅意庭院
青花瓷机甲
```

现在主题池 = 内置 100+ 条 + 你的 `topics.txt`。

---

## 相关文件

```
scripts/
├── daily_task.py             # 主脚本
├── daily_task.README.md      # 本文件
├── register_task.ps1         # 注册 Windows 计划任务
└── run_daily.bat             # Windows 一键执行

skills/
├── image_generator/
│   └── skill.py              # 生图（_save_image 命名规则）
├── image_curator/
│   ├── skill.py              # 鉴赏 + 写文章
│   └── writers.py            # make_heading 章节标题
└── wechat_formatter/
    ├── skill.py              # 微信排版 + 推送
    └── themes/               # 33 个排版主题 JSON

topics.txt                    # 自定义主题池（可选）
assets/qr/公众号结束处.png      # 文末二维码
```