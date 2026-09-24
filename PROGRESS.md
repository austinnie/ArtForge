# ArtForge 项目进度追踪

> 用于跨会话续作。每次会话结束前更新「当前进度」和「下一步」。
> 新会话开始时，先读本文件，再继续创作。

---

## 📌 项目概述

- **项目名**：ArtForge
- **定位**：东方艺术生成工坊（基于 PromptForge 架构重构）
- **目标主题**：
  - 🎎 日本文化（浮世绘、能剧、茶道、花道、武士、艺伎）
  - 👹 妖怪（百鬼夜行、天狗、河童、九尾狐、雪女、鬼灯）
  - 🖌️ 古风绘画（水墨、工笔、宋韵、青绿山水）
  - 📜 源氏物语（平安宫廷、十二单、屏风绘卷）
  - 🏯 唐风（敦煌壁画、唐仕女、飞天）
  - 🎨 艺术裸体（骨架已预留，具体内容待定）
- **作品特征**：画幅 + 题词 + 印章 + 年代感
- **项目路径**：`E:\SD_OpenVINO\ArtForge`

---

## ✅ 已完成

| 模块 | 文件 | 状态 | 备注 |
|------|------|------|------|
| 目录 | `scripts/create_project.py` | ✅ | 34 个子目录已定义 |
| 进度 | `PROGRESS.md` | ✅ | 本文档 |
| 配置 | `config/art_config.py` | ✅ | 画风/妖怪/唐风/画幅 已定义 |
| 配置 | `config/settings.py` | ✅ |完成 |
| 层 | `layers/__init__.py` | ✅ | 完成 |
| 层 | `layers/layer_scene.py` | ✅ | 25 个场景 |
| 层 | `layers/layer_style.py` | ✅ | 从 art_config 同步 ~29 画风 |
| 层 | `layers/layer_lighting.py` | ✅ | 25 个光影 |
| 层 | `layers/layer_inscription.py` | ✅ | 17 个题词印章 |
| 层 | `layers/layer_quality.py` | ✅ | 15 个画质 |
| 核心 | `core/prompt_builder.py` | ✅ | 已完成 |
| 核心 | `core/safety.py` | ⏳ | 待填（艺术豁免规则） |
| 核心 | `core/intent_analyzer.py` | ⏳ | 待填 |
| 服务 | `services/inscription_generator.py` | ⏳ | 待填（汉诗/和歌生成） |
| 服务 | `services/seal_generator.py` | ✅ | 朱文/白文，透明PNG，可贴图 |
| 服务 | `services/aging_processor.py` | ✅ | 宣纸/绢本/老纸/褐纸 + 5 种老化 |
| 服务 | `services/scroll_composer.py` | ⏳ | 待填（画幅合成） |
| 引擎 | `api_engines/__init__.py` | ✅ | 13 个引擎 + create_engine 工厂 |
| 引擎 | `api_engines/base.py` | ✅ | 基类 |
| 引擎 | `api_engines/agnes.py` | ✅ | Agnes（图像/文本/视频/视觉） |
| 引擎 | `api_engines/pollinations.py` | ✅ | Pollinations（免费，无需 Key） |
| 引擎 | `api_engines/siliconflow.py` | ✅ | 硅基流动 |
| 引擎 | 其余 10 个引擎 | ✅ | tongyi/yige/hunyuan/hf/freeapi/replicate/stability/free_multimodal_proxy/freellmapi/openrouter |
| 处理器 | `handlers/yokai_handler.py` | ⏳ | 待填（第一个） |
| 预设 | `presets/japanese/*` | ✅ | 5 个画风预设 |
| 预设 | `presets/gufeng/*` | ✅ | 5 个国画预设 |
| 预设 | `presets/genji/*` | ✅ | 5 个源氏预设 |
| 脚本 | `compose_artwork.py` | ✅ | 全流程合成 |
| 入口 | `test_pipeline.py` | ✅ | 最小链路验证脚本 |
| 说明 | `README.md` | ⏳ | 完成 |
| 配置 | `.env.sample` | ✅ | 环境变量样例 |
| 配置 | `requirements.txt` | ✅ | 依赖清单 |

---

## 🚧 当前进度

**正在做**：M3 后处理服务
**已完成**：印章生成器、做旧处理器
**下一步**：写 `services/inscription_generator.py`（题词生成，需 LLM + 降级方案）

---



## 📝 会话日志

### 2026-09-24 第 1 次会话

- ✅ 创建了 `scripts/create_project.py`
- ✅ 创建了 `PROGRESS.md`
- ✅ 创建了 `config/art_config.py`
- ⏭️ 敏感内容（art_nude）只留骨架
- **下次继续**：写 `config/settings.py` 和 `layers/__init__.py`

### 2026-09-24 第 2 次会话

- ✅ 完成 `config/settings.py` 和 `layers/__init__.py`

### 2026-09-24 第 3 次会话
- ✅ 6 层系统全部完成
  - subject 36 / scene 30 / style 29 / lighting 24
  - composition 8 / inscription 19 / quality 16
  - 合计 162 条短语

### 2026-09-24 第 4 次会话（续）
- ✅ 修复 PromptBuilder token 截断（从整层裁 → 逐短语裁）
- ✅ 修正 `layer_style.py`（去掉 yokai，style 从 29→19）
- ✅ `presets/yokai/tengu.py` — 第一个预设
- ✅ `compose_preset("tengu")` 验证通过
- **下次继续**：写更多妖怪预设 或 `core/safety.py`

### 2026-09-24 第 5 次会话
- ✅ 用户补充 `api_engines/` 全 13 个引擎 + `create_engine()` 工厂
- ✅ 新增 `test_pipeline.py`（预设 → prompt → 出图 → 保存）
- ✅ 新增 `.env.sample`、`requirements.txt`
- ✅ **M2 达成**：`python test_pipeline.py` 成功出天狗图
  - 水墨风、云海远山、题词印章齐全
  - 注意：题词/印章是 AI 画进图里的，非 PIL 合成（M3 要替换）


### 2026-09-24 第 6 次会话

- ✅ `services/seal_generator.py` — 印章生成器
  - 朱文（红字透底）/ 白文（红底白字），方形 + 引首章
  - 关键修复：`_plan_glyphs()` 预计算绝对坐标，消除逐字累积误差
  - 字号自适应：`_pick_font_size()` 分 square/rect 两套逻辑
  - 自检通过：鞍马山/天狗/源氏物语/百鬼夜行/天/ArtForge 均居中
- ✅ `services/aging_processor.py` — 做旧处理器
  - 四种纹理：宣纸 / 绢本 / 老纸 / 褐纸（程序生成，不依赖素材）
  - 五种效果：泛黄 / 霉斑 / 边缘磨损 / 暗角 / 噪点
  - 支持 seed 复现，已修 Pillow 13 DeprecationWarning
  - 自检通过：11 张对比图全部生成

### 2026-09-24 第 7 次会话
- ✅ `services/inscription_generator.py` — 题词生成器
  - 三层降级: Agnes → Pollinations → 内置诗句库
  - 修复 sys.path（services/ 下 import 不到 api_engines）
  - 修复 .env 加载（os.getenv 读不到 Key）
  - 自检通过: 8 主题 × 5 体裁，auto 模式 source=agnes
- ✅ **M3 完成**（seal + aging + inscription）

### 2026-09-24 第 8 次会话
- ✅ `compose_artwork.py` — 全流程合成
  - 预设 → 出图 → 做旧 → 题词 → 钤印 → 保存
  - InscriptionRenderer: 竖排从右往左 + 半透明白底衬
  - --clean-prompt 默认开（AI 只画画，题词印章交 PIL）
  - 印章放大 + 题词字号放大
- ✅ **M3 完成**，成品验收通过
- ⚠️ 已知小问题: 左上引首章英文（ArtForge）偏小，考虑改中文

### 2026-09-24 第 9 次会话
- ✅ 方案 A: --clean-prompt 剔除 inscription 层
- ✅ 题词无底衬(方案 B)，直接写在画上
- ✅ negative 追加禁文字印章词
- ✅ 引首章改中文「東方藝術」
- ✅ **M3 完成**，成品验收通过(乌鸦天狗立轴)
- ⚠️ 已知问题: AI 仍自画伪落款，视为风格特征接受

### 2026-09-24 第 10 次会话
- ✅ yokai 补全 5 个预设: tengu/kappa/kitsune/yuki_onna/oni
- ✅ 四张新预设全部出图成功
  - kappa 浮世绘最佳, yuki_onna 水墨最美
  - kitsune 偏动漫风, oni 偏西幻(训练数据带偏)
- ⚠️ 已知问题:
  1. 部分主题 style 层被 AI 现代风格盖过
  2. 右下主题印遇浅色背景对比不足

### 2026-09-24 第 11 次会话
- ✅ japanese 补全 5 个画风预设
  - byobu_e 屏风绘最佳(金箔+琳派)
  - nihonga 首次跑偏为唐风，加画家锚点(横山大观/东山魁夷)后修正
  - sumi_e 水墨留白教科书级
- 💡 关键经验: 用具体画家名锚定风格 > 流派术语
- ⚠️ 累积问题: 右下印浅背景对比不足 / AI 自画伪落款

### 2026-09-24 第 12 次会话
- ✅ gufeng 补全 5 个国画预设
  - shui_mo 水墨最佳(八大山人式孤舟)
  - gong_bi 工笔精细(牡丹层叠)
  - qing_lv 青绿出色(千里江山图味)
  - bai_miao 白描纯线描达成
  - jian_bi 画风对但题词主题脱节
- ⚠️ 累积问题:
  1. 右下印浅背景对比不足
  2. 引首章偶与 AI 伪落款重叠
  3. 画风预设题词 fallback 脱节(待 M5 加通用题跋主题)

### 2026-09-24 第 13 次会话
- ✅ genji 补全 5 个源氏物语预设
  - byobu_emaki 屏风绘卷最佳(金箔+六扇屏)
  - heian_court 平安宫廷氛围好(月下对饮)
  - moon_viewing 观月构图最美
  - junihitoe 十二单/ cherry_blossom 赏樱: 人物偏现代插画风
- 🔧 重构题词主题机制:
  - 新增「通用」主题(画风预设专用)
  - theme_from_preset 根据分类+预设名自动推主题
  - 修 PROMPT_TEMPLATES_GENERIC(「通用」不写进诗里)
  - Agnes 异常加日志(定位空返回问题)
- ⚠️ 累积问题:
  1. 平安美人脸偏现代 → 待 M5(古画锚点/换模型)
  2. 右下印浅背景对比不足
  3. 引首章偶与 AI 伪落款重叠
  4. Pollinations chat 403(Key 无 openai 权限，非阻塞)

### 2026-09-24 第 14 次会话
- ✅ tang 补全 5 个唐风预设
  - dunhuang 敦煌壁画 ⭐ 最佳(千佛+矿物颜料+墙面裂纹)
  - feitian 飞天 ⭐ 第二佳(反弹琵琶+飘带+月牙)
  - tang_palace 大唐宫苑 ✅(楼阁市井)
  - tang_beauty 唐仕女 ⚠️ 偏明清仕女(非唐代丰腴)
  - tang_horse 唐马 ⚠️ 偏写实(非韩幹工笔)
- ✅ **M4 完成**: 6 大主题各 5 个预设
- ⚠️ 累积问题(待 M5):
  1. 具体作品锚点(韩幹/周昉)AI 识别不稳，需换模型或 LoRA
  2. 唐风预设题词有时走日文，与画面脱节
  3. 平安/唐美人脸偏现代，非古画审美
  4. 右下印浅背景对比不足
- **下次继续**: M5 — 题词印章打磨 / 输出到微信



---

## 📋 下一步（按优先级）

### 阶段 A：配置与骨架
1. [ ] `config/settings.py` — 全局配置（复用 PromptForge 的 Settings 结构）
2. [ ] `layers/__init__.py` — 6 层定义与加载器
3. [ ] `layers/layer_subject.py` — 主体层

### 阶段 B：6 层系统
4. [ ] `layers/layer_scene.py` — 场景层
5. [ ] `layers/layer_style.py` — 画风层（浮世绘/日本画/水墨/工笔/敦煌）
6. [ ] `layers/layer_lighting.py` — 光影层
7. [ ] `layers/layer_composition.py` — 画幅层（立轴/横卷/屏风/团扇）
8. [ ] `layers/layer_inscription.py` — 题词印章层
9. [ ] `layers/layer_quality.py` — 画质层

### 阶段 C：核心引擎
10. [ ] `core/prompt_builder.py` — 6 层组合器
11. [ ] `core/safety.py` — 安全过滤（含艺术豁免）
12. [ ] `core/intent_analyzer.py` — 意图分析

### 阶段 D：服务
13. [ ] `services/inscription_generator.py` — 题词生成
14. [ ] `services/seal_generator.py` — 印章生成
15. [ ] `services/aging_processor.py` — 做旧处理
16. [ ] `services/scroll_composer.py` — 画幅合成

### 阶段 E：API 引擎
17. [ ] `api_engines/base.py` — 基类
18. [ ] `api_engines/agnes.py` — Agnes 引擎
19. [ ] `api_engines/pollinations.py` — Pollinations
20. [ ] `api_engines/siliconflow.py` — 硅基流动

### 阶段 F：处理器与预设
21. [ ] `handlers/yokai_handler.py` — 妖怪
22. [ ] `handlers/japanese_art_handler.py` — 日本文化
23. [ ] `handlers/gufeng_handler.py` — 古风
24. [ ] `handlers/genji_handler.py` — 源氏物语
25. [ ] `handlers/tang_handler.py` — 唐风
26. [ ] `presets/yokai/tengu.py` — 天狗（第一个预设）
27. [ ] 批量补充预设

### 阶段 G：入口与文档
28. [ ] `main.py`
29. [ ] `README.md`
30. [ ] `requirements.txt`
31. [ ] `.env.sample`

---

## 🎨 设计约定（不可更改，供后续会话遵守）

### 6 层提示词结构

| 层 | key | 说明 | 示例 |
|----|-----|------|------|
| 1 | `subject` | 主体 | 天狗、九尾狐、唐仕女 |
| 2 | `scene` | 场景 | 山林、宫廷、温泉、街道 |
| 3 | `style` | 画风 | 浮世绘、日本画、水墨、敦煌 |
| 4 | `lighting` | 光影 | 月光、烛火、晨雾、夕阳 |
| 5 | `composition` | 画幅 | 立轴、横卷、屏风、团扇 |
| 6 | `inscription` | 题词印章 | 书法、落款、朱印、做旧 |
| 7 | `quality` | 画质 | masterpiece, 8k, detailed |

### 画幅尺寸约定

| 画幅 | 比例 | 用途 |
|------|------|------|
| 立轴 | 9:16 | 单幅人物 / 花鸟 |
| 横卷 | 16:9 | 山水 / 故事 |
| 屏风 | 4:3 | 多扇组合 |
| 团扇 | 1:1 | 圆形小品 |
| 册页 | 3:4 | 组画 |

### 安全边界

- ✅ 允许：浮世绘春画风格、能剧面具、花魁、艺术人体（待细化）
- ❌ 禁止：现代色情、露骨性行为、未成年人
- 处理方式：`core/safety.py` 里加艺术豁免规则
- **敏感部分先跳过，留骨架和占位**


---

## 🔗 关键文件速查

| 用途 | 文件 |
|------|------|
| 6 层定义 | `layers/__init__.py` |
| 画风枚举 | `config/art_config.py` |
| 预设加载 | `preset_bridge.py`（待创建，从 PromptForge 抄） |
| 题词生成 | `services/inscription_generator.py` |
| 印章合成 | `services/seal_generator.py` |
| 做旧处理 | `services/aging_processor.py` |
| 画幅合成 | `services/scroll_composer.py` |

---

## 💡 技术备忘

- **API 引擎**：复用 PromptForge 的 `api_engines/`
  - Agnes（免费，推荐）
  - Pollinations（免费，无需 Key）
  - SiliconFlow（免费额度）
- **印章**：PIL 透明 PNG 叠加
- **做旧**：PIL 滤镜 + 噪点 + 边缘暗角
- **题词**：LLM 生成汉诗/和歌 → PIL 渲染书法字体
- **字体**：需准备毛笔字体（如"方正楷体"、"汉仪尚巍手书"）

---

## 📦 依赖清单（待完善）
```
核心
Pillow>=10.0.0
requests>=2.31.0
python-dotenv>=1.0.0

API
dashscope>=1.14.0 # 通义万相（可选）

图像处理
opencv-python>=4.10.0 # 做旧、滤镜
numpy>=1.26.0

可选
markdown>=3.5.0 # 微信排版
python-docx>=1.1.0 # Word 导出
```
