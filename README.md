# 🎎 ArtForge · 东方艺术生成工坊

> 用 AI 生成带**画幅、题词、印章、年代感**的东方艺术作品。
> 主题涵盖：日本文化 · 妖怪 · 古风绘画 · 源氏物语 · 唐风。

ArtForge 是一个基于 6 层提示词系统的艺术图像生成引擎。它把「主体 + 场景 + 画风 + 光影 + 画幅 + 题词印章」组合成完整 prompt，交给多家 AI 绘图 API 生成作品，再叠加**书法题词**、**朱红印章**、**做旧处理**，输出具有东方古典韵味的成品。

支持本地模型与云端 API 双模式，兼容 Agnes / Pollinations / SiliconFlow / HuggingFace 等多家引擎。

---

## ✨ 主要特性

### 🎨 6 层提示词系统

| 层 | 说明 | 示例 |
|----|------|------|
| `subject` | 主体 | 天狗、九尾狐、唐仕女 |
| `scene` | 场景 | 山林、宫廷、温泉、街道 |
| `style` | 画风 | 浮世绘、日本画、水墨、敦煌 |
| `lighting` | 光影 | 月光、烛火、晨雾、夕阳 |
| `composition` | 画幅 | 立轴、横卷、屏风、团扇 |
| `inscription` | 题词印章 | 书法、落款、朱印、做旧 |
| `quality` | 画质 | masterpiece, 8k, detailed |

> 实际是 7 层，沿用 LayerForge 的「6 层系统」命名习惯。

### 🖼️ 五类画幅

- **立轴**（9:16）— 单幅人物 / 花鸟
- **横卷**（16:9）— 山水 / 故事长卷
- **屏风**（4:3）— 多扇组合
- **团扇**（1:1）— 圆形小品
- **册页**（3:4）— 组画

### 🎭 六大主题

- 🎎 **日本文化** — 浮世绘、能剧、茶道、花道、武士、艺伎
- 👹 **妖怪** — 百鬼夜行、天狗、河童、九尾狐、雪女、鬼灯
- 🖌️ **古风绘画** — 水墨、工笔、宋韵、青绿山水
- 📜 **源氏物语** — 平安宫廷、十二单、屏风绘卷
- 🏯 **唐风** — 敦煌壁画、唐仕女、飞天
- 🎨 **艺术裸体** — 浮世绘春画风格、能剧面具、花魁（骨架已预留）

### 🖋️ 作品润色

- **题词生成** — LLM 生成汉诗 / 和歌 / 俳句 / 题跋
- **印章落款** — PIL 透明 PNG 叠加，支持朱文 / 白文
- **做旧处理** — 宣纸 / 绢本 / 老纸纹理 + 泛黄 + 霉斑 + 边缘磨损
- **画幅合成** — 自动加绫边 / 轴头 / 卷轴装裱

### 🔌 多 API 支持

| 引擎 | 免费 | 说明 |
|------|------|------|
| **Agnes AI** | ✅ | 推荐，需注册，图像 + 文本 + 视觉 |
| **Pollinations** | ✅ | 无需 Key，开箱即用 |
| **SiliconFlow** | ✅ | 免费额度，中文友好 |
| **HuggingFace** | ✅ | 免费限速 |
| **Replicate** | ❌ | 按量付费 |
| **Stability AI** | ❌ | 按量付费 |

---

## 🚀 快速开始

### 环境要求

- Python 3.8+
- 至少 8GB RAM
- 可选：Ollama（用于题词生成）
- 可选：FFmpeg（用于画幅合成导出）

### 安装

```bash
git clone <your-repo-url> ArtForge
cd ArtForge

python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac

pip install -r requirements.txt
```

### 配置

```bash
cp .env.sample .env
# 编辑 .env，填入 API Key
```

### 运行

```bash
python main.py
```

---

## 📖 使用指南

### 基本流程

1. **选择主题分类** — 日本文化 / 妖怪 / 古风 / 源氏 / 唐风
2. **选择画风预设** — 如 `ukiyo_e`（浮世绘）、`tengu`（天狗）
3. **指定画幅** — 立轴 / 横卷 / 屏风 / 团扇 / 册页
4. **生成图像** — 调用 API 出图
5. **润色** — 加题词 + 印章 + 做旧
6. **导出** — PNG / JPG / 微信图文

### 示例

```python
from core.prompt_builder import PromptBuilder
from api_engines import create_engine

# 1. 构建提示词
builder = PromptBuilder()
prompt = builder.compose(
    subject="tengu with long nose, red face, feathered wings",
    scene="deep mountain forest, misty peaks",
    style="ukiyo-e woodblock print",
    composition="vertical hanging scroll",
    inscription="calligraphy poem at top",
    quality="masterpiece, 8k",
)

# 2. 生成图像
engine = create_engine("agnes", {"AGNES_API_KEY": "..."})
image = engine.generate_single(prompt=prompt, width=768, height=1365)

# 3. 润色
from services.inscription_generator import InscriptionGenerator
from services.seal_generator import SealGenerator
from services.aging_processor import AgingProcessor

inscription = InscriptionGenerator().generate(theme="天狗", format="waka")
seal = SealGenerator().make("鞍马山")
image = AgingProcessor().apply(image, texture="xuan_paper")

# 4. 保存
image.save("output/yokai/tengu_001.png")
```

---

## 📁 项目结构

```text
ArtForge/
├── main.py                       # 入口
├── README.md
├── PROGRESS.md                   # 进度追踪（跨会话续作）
├── requirements.txt
├── .env.sample
│
├── config/
│   ├── settings.py               # 全局配置
│   └── art_config.py             # 画风 / 妖怪 / 唐风 / 画幅 / 题词印章
│
├── core/
│   ├── intent_analyzer.py        # 意图分析
│   ├── prompt_builder.py         # 6 层组合器
│   ├── context_manager.py        # 上下文
│   └── safety.py                 # 安全过滤（含艺术豁免）
│
├── layers/                       # 6 层提示词库
│   ├── layer_subject.py
│   ├── layer_scene.py
│   ├── layer_style.py
│   ├── layer_lighting.py
│   ├── layer_composition.py
│   ├── layer_inscription.py
│   └── layer_quality.py
│
├── presets/                      # 预设（按主题分类）
│   ├── japanese/
│   ├── yokai/
│   ├── gufeng/
│   ├── genji/
│   ├── tang/
│   └── art_nude/
│
├── handlers/                     # 意图处理器
│   ├── japanese_art_handler.py
│   ├── yokai_handler.py
│   ├── gufeng_handler.py
│   ├── genji_handler.py
│   ├── tang_handler.py
│   └── art_nude_handler.py
│
├── services/                     # 后处理服务
│   ├── inscription_generator.py  # 题词生成
│   ├── seal_generator.py         # 印章生成
│   ├── aging_processor.py        # 做旧处理
│   └── scroll_composer.py        # 画幅合成
│
├── api_engines/                  # API 引擎
│   ├── base.py
│   ├── agnes.py
│   ├── pollinations.py
│   ├── siliconflow.py
│   └── ...
│
├── skills/                       # 技能模块
│   ├── art_generator/
│   ├── art_curator/
│   ├── inscription_writer/
│   ├── seal_maker/
│   └── wechat_formatter/
│
├── assets/                       # 素材
│   ├── seals/zhu_wen/            # 朱文印
│   ├── seals/bai_wen/            # 白文印
│   ├── textures/xuan_paper/      # 宣纸
│   ├── textures/silk/            # 绢本
│   ├── textures/aged/            # 做旧
│   └── fonts/                    # 毛笔字体
│
├── output/                       # 输出
│   ├── japanese/
│   ├── yokai/
│   ├── gufeng/
│   ├── genji/
│   ├── tang/
│   └── art_nude/
│
└── scripts/
    ├── create_project.py         # 目录创建
    └── build_archive.py          # 归档
```

---

## 🎨 画风一览

### 日本文化

| Key | 名称 | 说明 |
|-----|------|------|
| `ukiyo_e` | 浮世绘 | 江户版画，平涂 + 粗线 |
| `nihonga` | 日本画 | 岩彩 + 金箔 |
| `sumi_e` | 水墨 | 禅意 + 留白 |
| `byobu_e` | 屏风绘 | 金屏风 + 装饰 |
| `emaki` | 绘卷物 | 大和绘 + 长卷 |

### 妖怪图鉴（部分）

| Key | 名称 |
|-----|------|
| `tengu` | 天狗 |
| `kappa` | 河童 |
| `kitsune` | 九尾狐 |
| `yuki_onna` | 雪女 |
| `oni` | 鬼 |
| `hyakki_yagyo` | 百鬼夜行 |
| `kitsune_no_yomeiri` | 狐狸嫁女 |
| `noppera_bo` | 野篦坊 |
| `roku_ro_kubi` | 辘轳首 |

### 古风

| Key | 名称 |
|-----|------|
| `shui_mo` | 水墨 |
| `gong_bi` | 工笔 |
| `qing_lv` | 青绿山水 |
| `jian_bi` | 减笔 |
| `bai_miao` | 白描 |

### 源氏物语

| Key | 名称 |
|-----|------|
| `heian_court` | 平安宫廷 |
| `junihitoe` | 十二单 |
| `byobu_emaki` | 屏风绘卷 |
| `moon_viewing` | 观月 |
| `cherry_blossom` | 赏樱 |

### 唐风

| Key | 名称 |
|-----|------|
| `dunhuang` | 敦煌壁画 |
| `tang_beauty` | 唐仕女 |
| `tang_palace` | 大唐宫苑 |
| `tang_horse` | 唐马 |

---

## 🖋️ 题词与印章

### 题词格式

- **汉诗** — 五言 / 七言
- **和歌** — 5-7-5-7-7
- **俳句** — 5-7-5
- **题跋** — 散文
- **款识** — 作者署名

### 印章

- **朱文印** — 阳刻，红字白底
- **白文印** — 阴刻，白字红底
- 位置：右下 / 左下 / 右上 / 左上

### 做旧

- 纸张：宣纸 / 绢本 / 老纸 / 褐纸
- 效果：霉斑 / 泛黄 / 折痕 / 边缘磨损 / 墨韵晕染

---

## 📦 依赖

核心依赖见 `requirements.txt`。主要：

```text
Pillow              # 图像处理
requests            # API 调用
python-dotenv       # 环境变量
opencv-python       # 做旧滤镜
numpy               # 数值
```

可选：

```text
markdown            # 微信排版
python-docx         # Word 导出
dashscope           # 通义万相
```

外部工具（可选）：

- **Ollama** — 题词生成（也可用 Agnes 替代）
- **FFmpeg** — 画幅合成导出

---

## 🔧 开发

### 添加新画风

1. 在 `config/art_config.py` 添加画风定义
2. 在 `layers/layer_style.py` 添加对应 prompt
3. 在 `presets/<分类>/` 添加预设文件
4. 提交

### 添加新妖怪

1. 在 `YOKAI_DICT` 添加条目
2. 在 `presets/yokai/` 添加预设
3. 提交

### 跨会话续作

读 `PROGRESS.md` → 看「当前进度」和「下一步」→ 继续创作 → 更新 `PROGRESS.md`。

---

## 🤝 贡献

欢迎提交 Issue 和 PR。

1. Fork 本仓库
2. 创建特性分支 `git checkout -b feature/xxx`
3. 提交 `git commit -m 'Add xxx'`
4. 推送 `git push origin feature/xxx`
5. 开启 PR

---

## 📝 许可证

MIT License

---

## 🙏 致谢

- **Stable Diffusion** — 扩散模型基础
- **Agnes AI** — 免费多模态 API
- **Pollinations** — 免费图像生成
- **LayerForge** — 6 层提示词系统灵感
- **PromptForge** — 架构参考

---

## ⚠️ 免责声明

本项目仅供学习和研究使用。

- 生成的艺术作品内容由用户输入的提示词决定
- 使用者需遵守相关法律法规和服务条款
- **艺术裸体类内容**：仅限传统东方美学范畴（浮世绘春画、能剧面具、花魁等），禁止现代色情、露骨性行为、未成年人内容
- 对于本地模式，请确保使用的模型符合其各自的许可协议

---

## 📮 联系

- 项目进度：见 `PROGRESS.md`
- Issue：GitHub Issues

---

## 🎯 里程碑

- [ ] **M1** — 6 层系统全部完成，能组合出提示词
- [ ] **M2** — 第一个预设（天狗）能出图
- [ ] **M3** — 题词 + 印章 + 做旧 全流程打通
- [ ] **M4** — 6 大主题各 5 个预设
- [ ] **M5** — 成品能输出到微信/知乎