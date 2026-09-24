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
| 配置 | `config/settings.py` | ⏳ | 待填 |
| 层 | `layers/__init__.py` | ⏳ | 待填 |
| 层 | `layers/layer_subject.py` | ⏳ | 待填 |
| 层 | `layers/layer_scene.py` | ⏳ | 待填 |
| 层 | `layers/layer_style.py` | ⏳ | 待填 |
| 层 | `layers/layer_lighting.py` | ⏳ | 待填 |
| 层 | `layers/layer_composition.py` | ⏳ | 待填（画幅） |
| 层 | `layers/layer_inscription.py` | ⏳ | 待填（题词印章） |
| 层 | `layers/layer_quality.py` | ⏳ | 待填 |
| 核心 | `core/prompt_builder.py` | ⏳ | 待填 |
| 核心 | `core/safety.py` | ⏳ | 待填（艺术豁免规则） |
| 核心 | `core/intent_analyzer.py` | ⏳ | 待填 |
| 服务 | `services/inscription_generator.py` | ⏳ | 待填（汉诗/和歌生成） |
| 服务 | `services/seal_generator.py` | ⏳ | 待填（印章渲染） |
| 服务 | `services/aging_processor.py` | ⏳ | 待填（做旧） |
| 服务 | `services/scroll_composer.py` | ⏳ | 待填（画幅合成） |
| 引擎 | `api_engines/__init__.py` | ⏳ | 待填（从 PromptForge 抄） |
| 处理器 | `handlers/yokai_handler.py` | ⏳ | 待填（第一个） |
| 预设 | `presets/yokai/tengu.py` | ⏳ | 待填（第一个） |
| 入口 | `main.py` | ⏳ | 待填 |
| 说明 | `README.md` | ⏳ | 待填 |

---

## 🚧 当前进度

**正在做**：`config/art_config.py` 刚完成
**下一步**：写 `config/settings.py` 和 `layers/__init__.py`

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

## 📝 会话日志

### 2026-09-24 第 1 次会话

- ✅ 创建了 `scripts/create_project.py`
- ✅ 创建了 `PROGRESS.md`
- ✅ 创建了 `config/art_config.py`
- ⏭️ 敏感内容（art_nude）只留骨架
- **下次继续**：写 `config/settings.py` 和 `layers/__init__.py`

### （新会话在此追加）

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
