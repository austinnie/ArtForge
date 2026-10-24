"""
github_repo_daily - 每天推荐一个 GitHub 仓库并生成文章发布到微信公众号

v1.3.0 改造要点：
  1. 【P0】强制文章第一行输出 `# H1`，并做标题黑名单校验，避免标题变成「痛点」
  2. 【P0】`_insert_illustrations` 依赖 H1，配合 v1.3.0 输出格式自动生效
  3. 【P1】先 `_classify_repo` 判断仓库类型（devtool/infra/app/library/tutorial），
     再按类型选场景模板 + 配图风格 + 排版主题
  4. 【P1】`_extract_scenario` 强制要求 role/pain 里的数字必须有 README 依据，
     找不到场景时返回空 JSON，由 `_generate_intro_article` 兜底
  5. 【P1】`generate_article` 的 scenario 为空时不再用 placeholder 硬拼，
     直接回退介绍文模式
  6. 【P2】封面优先级：本地高清图 > GitHub OG 图 > 第一张插图
  7. 【P2】主题按仓库类型映射（devtool/infra/library → github；app → magazine；
     tutorial → newspaper）
  8. 【P2】article.md 归档到 output/github_repo_daily/archive/YYYYMMDD/，
     不再只留在被清理的 tmp 里
"""

import os
import re
import json
import time
import base64
import random
import shutil
import logging
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# 标题黑名单：命中则替换为场景/描述推出的标题
TITLE_BLACKLIST = {"痛点", "简介", "前言", "背景", "概述", "实战复盘", "项目介绍", "关于"}

# 仓库类型 → 排版主题
THEME_BY_KIND = {
    "devtool":  "github",
    "infra":    "github",
    "library":  "github",
    "app":      "magazine",
    "tutorial": "newspaper",
}


class GitHubRepoDaily:
    name = "github_repo_daily"
    version = "1.3.0"

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self._setup_logging()
        self._setup_config()

    def _setup_logging(self):
        level = self.config.get("log_level", "INFO")
        logging.basicConfig(
            level=getattr(logging, level.upper()),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    def _setup_config(self):
        defaults = {
            "output_dir": str(PROJECT_ROOT / "output" / "github_repo_daily"),
            "history_file": "history.json",
            "github_token": os.environ.get("GITHUB_TOKEN", ""),
            # 若显式传入 wechat_theme，则不做类型映射
            "wechat_theme": None,
            "wechat_publish": True,
            "max_trending": 25,
            "log_level": "INFO",

            # 插图与文末二维码
            "illustration_count": 3,
            "illustration_engine": "agnes",
            "illustration_width": 1024,
            "illustration_height": 1024,
            "footer_image": "assets/qr/footer_tech.png",
            "footer_alt": "关注公众号",
        }
        for k, v in defaults.items():
            self.config.setdefault(k, v)
        Path(self.config["output_dir"]).mkdir(parents=True, exist_ok=True)

    # ---------- LLM 统一入口 ----------
    def _get_llm_backends(self) -> Optional[List[str]]:
        if self.config.get("llm_backends"):
            return list(self.config["llm_backends"])
        try:
            from config.settings import settings
            gh_backends = getattr(settings, "gh_daily_llm_backends", None)
            if gh_backends:
                return list(gh_backends)
        except Exception:
            pass
        return None

    def _llm_generate(
        self,
        prompt: str,
        *,
        temperature: float = None,
        max_tokens: int = None,
        timeout: int = None,
    ) -> str:
        from core.llm_client import get_default_client

        llm = get_default_client(
            backends=self._get_llm_backends(),
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            strict=False,
        )
        text = llm.generate(prompt)

        if text:
            logger.info(f"✅ LLM 返回 {len(text)} 字")
        else:
            logger.error("❌ 所有 LLM 后端均失败")
        return text

    # ---------- 历史记录 ----------
    def _load_history(self) -> List[str]:
        hist_file = Path(self.config["output_dir"]) / self.config["history_file"]
        if hist_file.exists():
            try:
                return json.loads(hist_file.read_text(encoding="utf-8"))
            except Exception:
                return []
        return []

    def _save_history(self, history: List[str]):
        hist_file = Path(self.config["output_dir"]) / self.config["history_file"]
        hist_file.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")

    # ---------- GitHub 相关 ----------
    def _github_headers(self):
        headers = {"Accept": "application/vnd.github.v3+json"}
        token = self.config.get("github_token")
        if token:
            headers["Authorization"] = f"token {token}"
        return headers

    def fetch_trending_repos(self) -> List[Dict[str, str]]:
        url = "https://github.com/trending?since=daily"
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        }

        html = ""
        try:
            resp = requests.get(url, headers=headers, timeout=20)
            resp.raise_for_status()
            html = resp.text
            logger.info(f"Trending 页面大小: {len(html)} 字符")
        except Exception as e:
            logger.error(f"抓取 trending 页面失败: {e}")

        repos: List[Dict[str, str]] = []
        seen = set()

        if html:
            blocks = re.findall(
                r'<article[^>]*class="[^"]*Box-row[^"]*"[^>]*>(.*?)</article>',
                html,
                re.DOTALL,
            )
            logger.info(f"匹配到 {len(blocks)} 个 Box-row 块")

            for block in blocks:
                m = re.search(r'<a\s+[^>]*href="/([^/"\s]+)/([^/"\s]+)"', block)
                if not m:
                    continue
                owner, repo = m.group(1), m.group(2)
                if owner in ("trending", "topics", "collections", "sponsors",
                             "login", "signup", "features", "marketplace"):
                    continue
                key = f"{owner}/{repo}"
                if key in seen:
                    continue
                seen.add(key)
                repos.append({"owner": owner, "repo": repo, "url": f"https://github.com/{key}"})
                if len(repos) >= self.config["max_trending"]:
                    break

        if not repos and html:
            logger.warning("Box-row 解析为空，改用宽松正则兜底")
            pattern = r'<h2[^>]*>\s*<a\s+[^>]*href="/([^/"\s]+)/([^/"\s]+)"'
            matches = re.findall(pattern, html, re.DOTALL)
            for owner, repo in matches[: self.config["max_trending"]]:
                if owner in ("trending", "topics", "collections"):
                    continue
                key = f"{owner}/{repo}"
                if key in seen:
                    continue
                seen.add(key)
                repos.append({"owner": owner, "repo": repo, "url": f"https://github.com/{key}"})

        if not repos:
            logger.warning("Trending 抓取失败，使用内置候选仓库")
            repos = [
                {"owner": "ollama", "repo": "ollama", "url": "https://github.com/ollama/ollama"},
                {"owner": "microsoft", "repo": "vscode", "url": "https://github.com/microsoft/vscode"},
                {"owner": "torvalds", "repo": "linux", "url": "https://github.com/torvalds/linux"},
                {"owner": "huggingface", "repo": "transformers", "url": "https://github.com/huggingface/transformers"},
                {"owner": "comfyanonymous", "repo": "ComfyUI", "url": "https://github.com/comfyanonymous/ComfyUI"},
            ]

        logger.info(f"获取到 {len(repos)} 个 trending 仓库")
        return repos

    def pick_repo(self, repos: List[Dict[str, str]]) -> Optional[Dict[str, str]]:
        history = self._load_history()
        random.shuffle(repos)
        for r in repos:
            key = f"{r['owner']}/{r['repo']}"
            if key not in history:
                return r
        return random.choice(repos) if repos else None

    def get_repo_details(self, owner: str, repo: str) -> Dict[str, Any]:
        api_base = "https://api.github.com"
        headers = self._github_headers()
        details = {}
        try:
            resp = requests.get(f"{api_base}/repos/{owner}/{repo}", headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                details.update({
                    "full_name": data.get("full_name"),
                    "description": data.get("description"),
                    "stars": data.get("stargazers_count"),
                    "forks": data.get("forks_count"),
                    "language": data.get("language"),
                    "topics": data.get("topics", []),
                    "html_url": data.get("html_url"),
                    "homepage": data.get("homepage"),
                })
            resp = requests.get(f"{api_base}/repos/{owner}/{repo}/readme", headers=headers, timeout=10)
            if resp.status_code == 200:
                readme_data = resp.json()
                content = readme_data.get("content", "")
                readme_text = base64.b64decode(content).decode("utf-8", errors="replace")
                details["readme"] = readme_text
            else:
                details["readme"] = ""
        except Exception as e:
            logger.error(f"获取仓库详情失败: {e}")
        return details

    # ---------- 仓库类型判断（新增） ----------

    def _classify_repo(self, repo_info: Dict[str, Any]) -> str:
        """
        判断仓库类型，用于后续选场景模板、配图风格、排版主题。

        返回值：devtool / infra / app / library / tutorial
        """
        full_name = repo_info.get("full_name", "")
        description = (repo_info.get("description") or "")[:300]
        topics = ", ".join(repo_info.get("topics", []))
        readme_head = (repo_info.get("readme") or "")[:1500]

        prompt = f"""判断这个 GitHub 仓库属于哪一类，只输出一个英文单词：
- devtool（开发者工具：CLI、SDK、agent 框架、IDE 插件、API 客户端）
- infra（基础设施：云服务、部署、监控、数据库、网络）
- app（应用：完整的用户可直接使用的产品）
- library（库：给其他项目调用的代码包）
- tutorial（教程/示例/学习资源）

仓库：{full_name}
描述：{description}
Topics：{topics}
README 开头：
{readme_head}

只输出单词（devtool / infra / app / library / tutorial）："""

        raw = self._llm_generate(prompt, temperature=0.1, max_tokens=20)
        kind = ""
        if raw:
            # 只取第一个单词
            token = re.split(r"[\s,。.]+", raw.strip())[0].lower()
            if token in ("devtool", "infra", "app", "library", "tutorial"):
                kind = token
        if not kind:
            kind = "devtool"
            logger.warning("⚠️ 仓库类型识别失败，默认按 devtool 处理")
        logger.info(f"🏷️ 仓库类型: {kind}")
        return kind

    # ---------- 场景抽取 ----------

    def _extract_scenario(self, repo_info: Dict[str, Any], repo_kind: str = "devtool") -> Dict[str, str]:
        """从 README + description 里抽出一个具体的「使用场景」。"""
        full_name = repo_info.get("full_name", "")
        description = repo_info.get("description", "") or ""
        readme = (repo_info.get("readme") or "")[:3000]
        topics = ", ".join(repo_info.get("topics", []))

        kind_hint = {
            "devtool":  "场景应该贴近 README 的 Quickstart / Getting Started / Example 段落，角色是'正在做某件事的工程师'。",
            "infra":    "场景应该贴近 README 的 Deploy / Setup / Architecture 段落，角色是'负责部署/运维的工程师'。",
            "app":      "场景应该贴近 README 的 Screenshot / Demo / Use Case 段落，角色是'这个产品的目标用户'。",
            "library":  "场景应该贴近 README 的 Integration / API / Example 段落，角色是'要集成这个库的开发者'。",
            "tutorial": "场景应该贴近 README 的 Learning Path / Chapter 段落，角色是'想学这个主题的初学者'。",
        }.get(repo_kind, "")

        prompt = f"""你是一个专业的 JSON 数据生成 API。你必须严格按照 JSON 格式输出，绝不能包含任何解释性文字。

【任务】
根据下面的 GitHub 仓库信息，提取一个具体的实战场景。

【约束】
- {kind_hint}
- role / pain / before 里的数字必须有 README 依据，找不到就写"未说明"。
- 如果找不到场景，只输出 {{}}。

【输出格式（必须严格遵循，不要用 Markdown 代码块包裹）】
{{
  "role": "谁在用（具体到职业+团队规模）",
  "pain": "具体痛点（带数字或具体动作）",
  "scene": "使用场景一句话",
  "before": "用之前流程（3-5步）",
  "after_hint": "README 声称的效果（没有写未说明）",
  "evidence": "场景依据"
}}

仓库：{full_name}
描述：{description}
Topics：{topics}
README 节选：
{readme}

JSON:"""

        raw = self._llm_generate(prompt, temperature=0.4, max_tokens=800)
        if not raw:
            return {}
            
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if not m:
            logger.warning(f"⚠️ 场景抽取：未找到 JSON 对象，原始返回 {len(raw)} 字")
            return {}
            
        try:
            data = json.loads(m.group())
        except Exception as e:
            logger.warning(f"⚠️ 场景 JSON 解析失败: {e}，原始返回: {raw[:200]}")
            return {}

        # ✅ 兼容多种字段命名（中英文/大小写/嵌套）
        role = data.get("role") or data.get("角色") or data.get("user") or ""
        pain = data.get("pain") or data.get("痛点") or data.get("problem") or ""
        scene = data.get("scene") or data.get("场景") or ""

        # ✅ 如果模型返回了嵌套结构（例如 {"scenario": {"role": "...", "pain": "..."}}）
        if not role and isinstance(data.get("scenario"), dict):
            nested = data["scenario"]
            role = nested.get("role") or nested.get("角色") or ""
            pain = nested.get("pain") or nested.get("痛点") or ""
            scene = nested.get("scene") or nested.get("场景") or ""

        # ✅ 如果依然缺失关键字段，打印日志方便排查，并返回空
        if not role or not pain:
            logger.warning(f"⚠️ 场景字段缺失：role={role!r}, pain={pain!r}，原始 keys: {list(data.keys())}")
            return {}

        # ✅ 构造标准返回结构
        return {
            "role": role,
            "pain": pain,
            "scene": scene or "日常开发里的一个环节",
            "before": data.get("before") or data.get("之前") or "未说明",
            "after_hint": data.get("after_hint") or data.get("效果") or "未说明",
            "evidence": data.get("evidence") or data.get("依据") or "基于 README 描述",
        }

    # ---------- 标题兜底工具 ----------

    @staticmethod
    def _fallback_title(repo_info: Dict[str, Any], scenario: Dict[str, str]) -> str:
        """场景/描述里推一个兜底标题。"""
        for candidate in (
            scenario.get("scene"),
            repo_info.get("description"),
            repo_info.get("full_name"),
        ):
            if candidate and str(candidate).strip():
                t = str(candidate).strip().rstrip("。.").replace("\n", " ")
                return t[:28]
        return "GitHub 仓库推荐"

    def _ensure_h1(self, article: str, repo_info: Dict[str, Any], scenario: Dict[str, str]) -> str:
        """
        确保文章第一行是 `# H1`，并做黑名单校验。
        """
        if not article:
            return article

        lines = article.split("\n", 1)
        first = lines[0].strip()
        rest = lines[1] if len(lines) > 1 else ""

        # 情况 1：第一行不是 H1
        if not first.startswith("# "):
            title = self._fallback_title(repo_info, scenario)
            logger.info(f"⚠️ 模型未输出 H1，已补标题: {title}")
            return f"# {title}\n\n{article.strip()}"

        # 情况 2：H1 命中黑名单
        h1 = first[2:].strip()
        if h1 in TITLE_BLACKLIST:
            better = self._fallback_title(repo_info, scenario)
            logger.info(f"⚠️ H1 命中黑名单「{h1}」，已替换为: {better}")
            return f"# {better}\n{rest}"

        return article

    # ---------- 文章生成 ----------

    def generate_article(
        self,
        repo_info: Dict[str, Any],
        scenario: Dict[str, str] = None,
        repo_kind: str = "devtool",
    ) -> str:
        """生成“实战复盘文”，scenario 为空时回退到介绍文。"""
        scenario = scenario or {}

        # P1-3：scenario 为空时不要用 placeholder 硬拼，直接走介绍文
        if not scenario.get("role") or not scenario.get("pain"):
            logger.warning("⚠️ 场景抽取为空，回退到介绍文模式")
            return self._generate_intro_article(repo_info)

        full_name = repo_info.get("full_name", "未知仓库")
        description = repo_info.get("description", "")
        stars = repo_info.get("stars", 0)
        language = repo_info.get("language", "")
        topics = ", ".join(repo_info.get("topics", []))
        readme = (repo_info.get("readme") or "")[:4000]
        html_url = repo_info.get("html_url", "")

        role = scenario["role"]
        pain = scenario["pain"]
        scene = scenario.get("scene", "日常开发里的一个环节")
        before = scenario.get("before", "未说明")
        after_hint = scenario.get("after_hint", "未说明")
        evidence = scenario.get("evidence", "基于 README 描述")

        prompt = f"""你是一个在一线写代码的工程师，现在要写一篇公众号文章。**这不是项目介绍文，而是"我用这个仓库解决了什么具体问题"的实战复盘。**

写作约束（很重要，违反任何一条都会让文章变成 AI 味很重的介绍文）：
1. **禁止**写"XX 是一个开源的……它支持……它有以下亮点"这种介绍体。
2. 全文围绕**一个场景**展开：{role} 遇到「{pain}」，用这个仓库把「{scene}」这件事跑通。
3. 结构必须按下面 6 段来，每段用 ## 二级标题：
   - ## 痛点：一个具体的麻烦（复述 {pain}，写出具体动作和耗时）
   - ## 之前我们是怎么做的（{before}，3-5 步，写出笨拙感）
   - ## 为什么最后选了这个项目（对比 2 个替代方案，说清楚取舍）
   - ## 关键步骤（3-5 步，每步说清楚"做什么、为什么这么做"，不用贴完整代码，用伪代码或命令名即可）
   - ## 跑完之后（写结果，但**只写 README 能支撑的部分**；README 没说的效果不要编数字，用"按项目文档描述，可以……"这种句式）
   - ## 适合谁 / 不适合谁（明确边界，别当广告）
4. 全文 1200—1800 字，中文，语气像在技术群里跟同事讲，不要用"赋能""闭环""抓手"这类词。
5. **诚实优先**：你没有实际跑过这个项目，所以凡是"实测数字"都不能编。要么用"README 里写的是……"，要么用"按文档描述……"。文章结尾加一行小字：`> 本文基于 {full_name} 的 README 与公开信息整理，未做完整实测，关键步骤仅供参考。`
6. 标题要具体，不要包含"推荐""盘点""必看"这类词，格式参考：
   - `用 {full_name} 把 {pain} 从 X 小时压到 Y 分钟`
   - `{role} 不想再 {pain}，于是用了 {full_name}`
   - 如果确实写不出数字，就用：`{role} 是怎么用 {full_name} 解决 {scene} 的`

仓库信息（供你核对事实，不要把这段原样抄进文章）：
- 仓库：{full_name}
- 描述：{description}
- Star：{stars}
- 语言：{language}
- Topics：{topics}
- 场景依据：{evidence}
- README 声称效果：{after_hint}
- 链接：{html_url}

README 节选（事实来源，只引用能支撑文章的部分）：
{readme}

现在直接输出文章。**第一行必须是 `# 标题`**（Markdown H1，标题里不要有"推荐""盘点""必看"这类词，也不要用"痛点/简介/前言/背景/概述"作为标题），从第二行开始是正文。正文的 6 个小节用 `##` 二级标题。"""

        article = self._llm_generate(prompt, temperature=0.7, max_tokens=3500)

        if article:
            article = re.sub(r"^```(?:markdown|md)?\s*\n", "", article)
            article = re.sub(r"\n```\s*$", "", article)
            article = article.strip()
            # P0-1：确保 H1 存在且合法
            article = self._ensure_h1(article, repo_info, scenario)
            return article

        logger.warning("⚠️ 所有 LLM 均失败，使用基础模板")
        return self._generate_intro_article(repo_info)

    def _generate_intro_article(self, repo_info: Dict[str, Any]) -> str:
        """介绍文兜底（scenario 抽取失败 / LLM 失败时用）。"""
        full_name = repo_info.get("full_name", "未知仓库")
        description = repo_info.get("description", "")
        stars = repo_info.get("stars", 0)
        language = repo_info.get("language", "")
        topics = ", ".join(repo_info.get("topics", []))
        readme = (repo_info.get("readme") or "")[:4000]
        html_url = repo_info.get("html_url", "")

        prompt = f"""你是一个技术博主，请根据以下 GitHub 仓库信息，写一篇介绍文章。
要求：
1. 标题吸引人，**第一行必须输出 `# 标题`**（Markdown H1），不要用"推荐/盘点/必看/简介/前言"作为标题。
2. 介绍仓库的主要功能、用途、亮点。
3. 语言通俗易懂，适合公众号读者。
4. 可以包含使用场景、技术栈等。
5. 文章长度 800-1200 字。
6. 输出 Markdown 格式，正文用 ## 二级标题分节。
7. 只输出文章正文，不要任何前言/解释/代码块围栏。

仓库名称：{full_name}
仓库描述：{description}
Star 数：{stars}
主要语言：{language}
标签：{topics}

README 内容（节选）：
{readme}

请开始写文章（第一行 `# 标题`）："""

        article = self._llm_generate(prompt, temperature=0.7, max_tokens=2048)
        if article:
            article = re.sub(r"^```(?:markdown|md)?\s*\n", "", article)
            article = re.sub(r"\n```\s*$", "", article)
            article = article.strip()
            article = self._ensure_h1(article, repo_info, {})
            return article

        # 极端兜底：纯模板
        return (
            f"# {full_name}\n\n"
            f"{description}\n\n"
            f"- Star: {stars}\n"
            f"- 语言: {language}\n"
            f"- 标签: {topics}\n\n"
            f"更多详情请访问：{html_url}\n"
        )

    # ---------- 插图 prompt 提炼 ----------

    def _generate_illustration_prompts(
        self,
        repo_info: Dict[str, Any],
        article: str,
        count: int = 3,
        repo_kind: str = "devtool",
    ) -> List[str]:
        if count <= 0:
            return []

        full_name = repo_info.get("full_name", "")
        article_excerpt = article[:800].replace("\n", " ")

        # 按仓库类型给配图风格
        # 按仓库类型给配图风格（移除容易生成乱码的图表类词汇）
        style_hint = {
            "devtool": "abstract tech illustration, geometric shapes, glowing nodes, cyber security concept, dark background, no text, no UI",
            "infra":   "cloud infrastructure concept art, glowing server nodes, data streams, high tech, no text, no charts",
            "app":     "clean product concept illustration, soft gradients, flat design, light background, no text, no screenshot",
            "library": "abstract modular structure, glowing 3D blocks, isometric tech art, clean background, no text, no code",
            "tutorial":"learning journey concept, floating books and abstract lightbulbs, flat design, no text",
        }.get(repo_kind, "clean technical illustration, light background, no text")
        
        prompt = f"""You are an illustrator. Based on the following tech article, write {count} English prompts for AI image generation.
Requirements:
1. Each prompt <= 30 English words.
2. Style: {style_hint}.
3. Theme should relate to the repo's purpose or use case.
4. **STRICT RULE: Absolutely NO TEXT, NO LETTERS, NO WORDS, NO CODE, NO FLOWCHARTS with boxes.** Use only abstract shapes and glowing lines.
5. Output ONLY a JSON array, e.g.: ["prompt 1", "prompt 2", "prompt 3"]

Repo: {full_name}
Article excerpt: {article_excerpt}

JSON array:"""

        raw = self._llm_generate(prompt, temperature=0.8, max_tokens=500)

        if raw:
            m = re.search(r"\[.*\]", raw, re.DOTALL)
            if m:
                try:
                    arr = json.loads(m.group())
                    arr = [str(x).strip() for x in arr if str(x).strip()]
                    if arr:
                        return arr[:count]
                except json.JSONDecodeError:
                    pass

        return [
            f"abstract tech diagram inspired by {full_name}, clean minimal, "
            f"light background, no text, no code"
        ]

    # ---------- 插图生成 ----------

    def _generate_illustrations(self, prompts: List[str], save_dir: Path) -> List[Path]:
        if not prompts:
            return []

        save_dir.mkdir(parents=True, exist_ok=True)
        paths: List[Path] = []

        try:
            from api_engines import create_engine
            from config.settings import settings

            engine_name = self.config.get("illustration_engine", "agnes")

            if engine_name == "agnes":
                engine_cfg = {
                    "AGNES_API_KEY": settings.agnes_api_key,
                    "AGNES_BASE_URL": settings.agnes_base_url,
                    "AGNES_IMAGE_MODEL": settings.agnes_image_model,
                }
            elif engine_name == "pollinations":
                engine_cfg = {"POLLINATIONS_MODEL": settings.pollinations_model}
            elif engine_name == "siliconflow":
                engine_cfg = {
                    "SILICONFLOW_API_KEY": settings.siliconflow_api_key,
                    "SILICONFLOW_MODEL": settings.siliconflow_model,
                }
            else:
                logger.warning(f"不支持的插图引擎: {engine_name}")
                return []

            engine = create_engine(engine_name, engine_cfg)
            if engine is None:
                logger.warning(f"插图引擎初始化失败: {engine_name}")
                return []

            w = self.config["illustration_width"]
            h = self.config["illustration_height"]

            for i, prompt in enumerate(prompts, 1):
                try:
                    logger.info(f"🎨 生成插图 [{i}/{len(prompts)}]: {prompt[:60]}...")
                    img = engine.generate_single(
                        prompt=prompt,
                        negative="text, watermark, signature, ui, code, letters, words, numbers, logo",
                        width=w,
                        height=h,
                        steps=20,
                        cfg=7.5,
                    )
                    path = save_dir / f"illustration_{i:02d}.png"
                    img.save(path, "PNG", optimize=True)
                    paths.append(path)
                    time.sleep(1)
                except Exception as e:
                    logger.warning(f"⚠️ 插图 {i} 生成失败: {e}")
                    continue
        except Exception as e:
            logger.error(f"❌ 插图生成流程异常: {e}")

        return paths

    # ---------- 插图插入（P0-2） ----------

    def _insert_illustrations(self, article: str, image_paths: List[Path]) -> str:
        """
        插入规则：
          - H1 后插 1 张（如果有）
          - 每个 `## ` 后插 1 张（直到用完）
          - 剩下的图不再堆文末，丢弃并记 warning
        """
        if not image_paths:
            return article

        lines = article.split("\n")
        result: List[str] = []
        img_idx = 0
        n = len(image_paths)
        head_seen = False

        for line in lines:
            if (not head_seen) and line.startswith("# ") and not line.startswith("## "):
                result.append(line)
                if img_idx < n:
                    result.extend(["", f"![illustration](assets/{image_paths[img_idx].name})", ""])
                    img_idx += 1
                head_seen = True
                continue

            if line.startswith("## ") and img_idx < n:
                result.extend(["", f"![illustration](assets/{image_paths[img_idx].name})", ""])
                img_idx += 1

            result.append(line)

        if img_idx < n:
            # 只在文末补 1 张，其余丢弃
            result.extend(["", f"![illustration](assets/{image_paths[img_idx].name})", ""])
            if n - img_idx - 1 > 0:
                logger.warning(f"⚠️ 有 {n - img_idx - 1} 张插图未能插入，已丢弃")

        return "\n".join(result)

    # ---------- 封面（P2-3） ----------

    def _fetch_cover_image(self, repo_info: Dict[str, Any], save_dir: Path) -> Optional[Path]:
        """
        封面优先级：
          1. 本地高清图 output/github_repo_daily/covers/{owner}_{repo}.png
          2. GitHub Open Graph 图
        """
        full_name = repo_info.get("full_name") or ""
        if "/" not in full_name:
            return None

        owner, repo = full_name.split("/", 1)

        # 1) 本地高清图
        local_cover = Path(self.config["output_dir"]) / "covers" / f"{owner}_{repo}.png"
        if local_cover.exists():
            logger.info(f"✅ 使用本地高清封面: {local_cover}")
            return local_cover

        # 2) GitHub OG 图
        og_url = f"https://opengraph.githubassets.com/1/{owner}/{repo}"
        save_dir.mkdir(parents=True, exist_ok=True)
        cover_path = save_dir / "cover.png"

        try:
            from PIL import Image
            import io as _io

            resp = requests.get(og_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
            resp.raise_for_status()
            img = Image.open(_io.BytesIO(resp.content)).convert("RGB")

            w, h = img.size
            target_ratio = 2.35
            if w / h > target_ratio:
                new_w = int(h * target_ratio)
                left = (w - new_w) // 2
                img = img.crop((left, 0, left + new_w, h))
            else:
                new_h = int(w / target_ratio)
                top = (h - new_h) // 2
                img = img.crop((0, top, w, top + new_h))

            img = img.resize((900, 383), Image.Resampling.LANCZOS)
            img.save(cover_path, "PNG", optimize=True)
            return cover_path
        except Exception as e:
            logger.warning(f"⚠️ 封面下载/处理失败: {e}")
            return None

    # ---------- 发布到微信 ----------

    def publish_to_wechat(
        self,
        article_md: str,
        repo_info: Optional[Dict[str, Any]] = None,
        cover_image: Optional[Path] = None,
        work_dir: Optional[Path] = None,
        theme: Optional[str] = None,
    ) -> bool:
        try:
            from skills.wechat_formatter import WechatFormatter

            if work_dir is None:
                work_dir = Path(self.config["output_dir"]) / "tmp" / datetime.now().strftime("%Y%m%d_%H%M%S")
            work_dir = Path(work_dir)
            assets_dir = work_dir / "assets"
            assets_dir.mkdir(parents=True, exist_ok=True)

            if cover_image and cover_image.exists():
                target = assets_dir / cover_image.name
                if cover_image != target and not target.exists():
                    shutil.copy2(cover_image, target)

            md_file = work_dir / "article.md"
            if not md_file.exists():
                md_file.write_text(article_md, encoding="utf-8")

            # ✅ 封面：调用方已做优先级选择
            cover_path = cover_image if cover_image and cover_image.exists() else None

            footer_path = self._get_footer_image()

            fmt = WechatFormatter()
            fmt_kwargs = {
                "theme": theme or self.config.get("wechat_theme") or "newspaper",
                "open": False,
            }
            if footer_path and footer_path.exists():
                fmt_kwargs["footer_image"] = str(footer_path)
                fmt_kwargs["footer_alt"] = self.config["footer_alt"]

            result = fmt.format(str(md_file), **fmt_kwargs)
            if result.get("status") != "success":
                logger.error(f"排版失败: {result.get('error')}")
                return False

            article_dir = Path(result["result"]["article_dir"])

            if self.config.get("wechat_publish", True):
                if cover_path and cover_path.exists():
                    images_dir = article_dir / "images"
                    images_dir.mkdir(parents=True, exist_ok=True)
                    target = images_dir / cover_path.name
                    if not target.exists():
                        shutil.copy2(cover_path, target)

                pub_result = fmt.publish(str(article_dir))
                if pub_result.get("status") == "success":
                    logger.info("✅ 已发布到公众号草稿箱")
                    return True
                else:
                    logger.error(f"❌ 发布失败: {pub_result.get('error')}")
                    return False
            else:
                logger.info(f"排版完成，未发布。输出目录: {article_dir}")
                return False   # 👈 这里改回 False，代表「没有发布」

        except Exception as e:
            logger.error(f"发布到微信失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _get_footer_image(self) -> Optional[Path]:
        rel = self.config.get("footer_image")
        if not rel:
            return None
        p = Path(rel)
        if not p.is_absolute():
            p = PROJECT_ROOT / p
        return p if p.exists() else None

    # ---------- 主入口 ----------

    def execute(self, **kwargs) -> Dict[str, Any]:
        start_time = time.time()
        logger.info(f"执行技能: {self.name} (v{self.version})")

        work_dir: Optional[Path] = None
        archive_md: Optional[Path] = None

        try:
            repos = self.fetch_trending_repos()
            if not repos:
                return {"status": "error", "error": "未获取到任何仓库"}

            repo = self.pick_repo(repos)
            if not repo:
                return {"status": "error", "error": "没有可用仓库"}

            owner, repo_name = repo["owner"], repo["repo"]
            full_name = f"{owner}/{repo_name}"
            logger.info(f"今日推荐: {full_name}")

            details = self.get_repo_details(owner, repo_name)
            if not details.get("full_name"):
                return {"status": "error", "error": f"无法获取仓库详情: {full_name}"}

            # 1) 仓库类型
            repo_kind = self._classify_repo(details)

            # 2) 场景抽取
            scenario = self._extract_scenario(details, repo_kind=repo_kind)
            logger.info(
                f"🎯 场景抽取: {scenario.get('role', '（空，走介绍文）')} / "
                f"{scenario.get('pain', '')}"
            )

            # 3) 生成文章
            article = self.generate_article(details, scenario=scenario, repo_kind=repo_kind)
            if not article:
                return {"status": "error", "error": "文章生成失败"}

            work_dir = Path(self.config["output_dir"]) / "tmp" / datetime.now().strftime("%Y%m%d_%H%M%S")
            assets_dir = work_dir / "assets"
            assets_dir.mkdir(parents=True, exist_ok=True)

            # 4) 插图
            illustration_paths: List[Path] = []
            try:
                prompts = self._generate_illustration_prompts(
                    details, article, count=self.config["illustration_count"], repo_kind=repo_kind,
                )
                if prompts:
                    illustration_paths = self._generate_illustrations(prompts, assets_dir)
            except Exception as e:
                logger.warning(f"⚠️ 插图流程失败，继续无图文章: {e}")

            if illustration_paths:
                article = self._insert_illustrations(article, illustration_paths)

            md_file = work_dir / "article.md"
            md_file.write_text(article, encoding="utf-8")

            # 5) 封面（P2-3：本地高清 > OG 图 > 第一张插图）
            cover = self._fetch_cover_image(details, assets_dir)
            if not cover and illustration_paths:
                cover = illustration_paths[0]

            # 6) 主题（P2-2）
            theme = self.config.get("wechat_theme") or THEME_BY_KIND.get(repo_kind, "newspaper")
            logger.info(f"🎨 排版主题: {theme}")

            illustration_str_paths = [str(p) for p in illustration_paths]

            # 7) 发布
            # 7) 发布
            published = self.publish_to_wechat(
                article_md=article,
                repo_info=details,
                cover_image=cover,
                work_dir=work_dir,
                theme=theme,
            )

            # 8) 归档（P2-1）
            archive_dir = PROJECT_ROOT / "output" / "github_repo_daily" / "archive" / datetime.now().strftime("%Y%m%d")
            archive_dir.mkdir(parents=True, exist_ok=True)
            archive_md = archive_dir / f"{repo_name}.md"
            try:
                shutil.copy2(md_file, archive_md)
                logger.info(f"📦 已归档: {archive_md}")
            except Exception as e:
                logger.warning(f"⚠️ 归档失败: {e}")
                archive_md = md_file

            history = self._load_history()
            if full_name not in history:
                history.append(full_name)
                self._save_history(history)

            elapsed = time.time() - start_time
            
            # ✅ 修复：根据是否要求发布来判定状态
            if published:
                status = "success"
            elif not self.config.get("wechat_publish", True):
                status = "success"  # 本来就不要求发布，排版成功就算成功
            else:
                status = "partial_success"  # 要求发布但失败了

            return {
                "status": status,
                "result": {
                    "repo": full_name,
                    "repo_url": details.get("html_url"),
                    "repo_kind": repo_kind,
                    "theme": theme,
                    "article_path": str(archive_md),
                    "illustrations": illustration_str_paths,
                    "published": published,
                    "elapsed": f"{elapsed:.2f}s",
                },
                "metadata": {"skill": self.name, "version": self.version},
            }

        except Exception as e:
            logger.error(f"执行失败: {e}")
            import traceback
            traceback.print_exc()
            return {"status": "error", "error": str(e), "skill": self.name}

        finally:
            if work_dir is not None:
                try:
                    if work_dir.exists():
                        shutil.rmtree(work_dir, ignore_errors=True)
                        logger.info(f"🧹 已清理临时目录: {work_dir}")
                except Exception as e:
                    logger.warning(f"⚠️ 清理临时目录失败: {e}")