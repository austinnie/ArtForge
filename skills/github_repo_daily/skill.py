"""
github_repo_daily - 每天推荐一个 GitHub 仓库并生成文章发布到微信公众号

流程：
  1. 抓取 GitHub Trending 每日榜单
  2. 挑选一个未推荐过的仓库
  3. 调用 GitHub API 获取仓库详情与 README
  4. 【新增】基于 README 抽取具体的业务场景 (角色、痛点、场景)
  5. 使用 LLMClient 生成“实战复盘文”
  6. 调用 wechat_formatter 排版并发布到公众号草稿箱
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


class GitHubRepoDaily:
    name = "github_repo_daily"
    version = "1.2.0"   # ✅ 升级版本，支持实战复盘文

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
            "wechat_theme": "newspaper",
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

    # ---------- 场景抽取 ----------

    def _extract_scenario(self, repo_info: Dict[str, Any]) -> Dict[str, str]:
        """从 README + description 里抽出一个具体的「使用场景」。"""
        full_name = repo_info.get("full_name", "")
        description = repo_info.get("description", "") or ""
        readme = (repo_info.get("readme") or "")[:3000]
        topics = ", ".join(repo_info.get("topics", []))

        prompt = f"""你是一个技术编辑。下面是一个 GitHub 仓库的信息。请从 README 里找出**一个**最具体、最能打动人的使用场景，用它来写一篇"场景实战文"，而不是"项目介绍文"。

要求：
1. 角色要具体：不要写"开发者"，要写"做跨境电商独立站的 3 人小团队"、"给客户做交付的外包公司前端"这种。
2. 痛点要具体：不要写"效率低"，要写"每次上新 200 个 SKU 要手动改 3 小时 Excel"。
3. 场景要能从 README 里找到依据（README 提到的 use case、example、screenshot 说明都算）。
4. 如果 README 里找不到具体场景，就选一个**最贴近该仓库能力边界**的真实使用场景，并在 "evidence" 字段写清楚"这是推测，依据是 XX 功能"。
5. 只输出 JSON，不要任何解释，不要用 Markdown 代码块。

仓库：{full_name}
描述：{description}
Topics：{topics}
README 节选：
{readme}

输出 JSON 格式：
{{
  "role": "谁在用（具体到职业+团队规模）",
  "pain": "具体痛点（带数字或具体动作）",
  "scene": "使用场景一句话",
  "before": "用之前他们的流程是怎样的（3-5 步）",
  "after_hint": "README 声称用完之后的效果（如果没有就写'未说明'）",
  "evidence": "这个场景的依据：README 的哪句话 / 哪个 example / 或'推测，依据是 XX 功能'"
}}"""

        raw = self._llm_generate(prompt, temperature=0.4, max_tokens=800)
        if not raw:
            return {}
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if not m:
            return {}
        try:
            return json.loads(m.group())
        except Exception:
            logger.warning(f"场景 JSON 解析失败: {raw[:100]}")
            return {}

    # ---------- 文章生成 ----------

    def generate_article(self, repo_info: Dict[str, Any], scenario: Dict[str, str] = None) -> str:
        """生成“实战复盘文”，而不是“项目介绍文”。"""
        full_name = repo_info.get("full_name", "未知仓库")
        description = repo_info.get("description", "")
        stars = repo_info.get("stars", 0)
        language = repo_info.get("language", "")
        topics = ", ".join(repo_info.get("topics", []))
        readme = (repo_info.get("readme") or "")[:4000]
        html_url = repo_info.get("html_url", "")

        scenario = scenario or {}
        role = scenario.get("role", "一个开发者")
        pain = scenario.get("pain", "一个重复性很高的手动流程")
        scene = scenario.get("scene", "日常开发里的一个环节")
        before = scenario.get("before", "手动处理，步骤多、易出错")
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

现在直接输出文章，第一行是标题（不要加 # 号），从第二行开始是正文。"""

        # 长文，token 给到 3500
        article = self._llm_generate(prompt, temperature=0.7, max_tokens=3500)

        if article:
            article = re.sub(r"^```(?:markdown|md)?\s*\n", "", article)
            article = re.sub(r"\n```\s*$", "", article)
            return article.strip()

        logger.warning("⚠️ 所有 LLM 均失败，使用基础模板")
        return f"# {full_name}\n\n{description}\n\n- Star: {stars}\n- 语言: {language}\n\n更多详情：{html_url}\n"

    # ---------- 插图 prompt 提炼 ----------

    def _generate_illustration_prompts(
        self,
        repo_info: Dict[str, Any],
        article: str,
        count: int = 3,
    ) -> List[str]:
        if count <= 0:
            return []

        full_name = repo_info.get("full_name", "")
        article_excerpt = article[:800].replace("\n", " ")

        prompt = f"""You are an illustrator. Based on the following tech article, write {count} English prompts for AI image generation.
Requirements:
1. Each prompt <= 30 English words.
2. Style: clean technical diagram / flow chart / isometric illustration, light background, no text, no UI mockup, suitable for a "before vs after" workflow article.
3. Theme should relate to the repo's purpose or use case.
4. Output ONLY a JSON array, e.g.: ["prompt 1", "prompt 2", "prompt 3"]

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

        return [f"abstract tech diagram inspired by {full_name}, clean minimal, workflow concept, light background, no text"]

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
                return []

            engine = create_engine(engine_name, engine_cfg)
            if engine is None:
                return []

            w = self.config["illustration_width"]
            h = self.config["illustration_height"]

            for i, prompt in enumerate(prompts, 1):
                try:
                    logger.info(f"🎨 生成插图 [{i}/{len(prompts)}]: {prompt[:60]}...")
                    img = engine.generate_single(
                        prompt=prompt,
                        negative="text, watermark, signature, ui, code, blurry, noisy",
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

    def _insert_illustrations(self, article: str, image_paths: List[Path]) -> str:
        if not image_paths:
            return article

        lines = article.split("\n")
        result: List[str] = []
        img_idx = 0
        n_images = len(image_paths)
        head_seen = False

        for line in lines:
            if (not head_seen) and line.startswith("# ") and not line.startswith("## "):
                result.append(line)
                if img_idx < n_images:
                    result.extend(["", f"![illustration](assets/{image_paths[img_idx].name})", ""])
                    img_idx += 1
                head_seen = True
                continue

            if line.startswith("## ") and img_idx < n_images:
                result.extend(["", f"![illustration](assets/{image_paths[img_idx].name})", ""])
                img_idx += 1

            result.append(line)

        if img_idx < n_images:
            result.append("")
            for p in image_paths[img_idx:]:
                result.extend([f"![illustration](assets/{p.name})", ""])

        return "\n".join(result)

    # ---------- 封面 ----------

    def _fetch_cover_image(self, repo_info: Dict[str, Any], save_dir: Path) -> Optional[Path]:
        full_name = repo_info.get("full_name") or ""
        if "/" in full_name:
            owner, repo = full_name.split("/", 1)
            # ✅ 优先使用本地手动配置的高清截图封面
            local_cover = Path(self.config["output_dir"]) / "covers" / f"{owner}_{repo}.png"
            if local_cover.exists():
                logger.info(f"✅ 使用本地高清封面: {local_cover}")
                return local_cover

        if "/" not in full_name:
            return None
        owner, repo = full_name.split("/", 1)
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

            cover_path = cover_image if cover_image and cover_image.exists() else None
            if not cover_path and repo_info:
                cover_path = self._fetch_cover_image(repo_info, assets_dir)

            footer_path = self._get_footer_image()

            fmt = WechatFormatter()
            fmt_kwargs = {"theme": self.config["wechat_theme"], "open": False}
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
                return True

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

            # ✅ 1. 抽取场景
            scenario = self._extract_scenario(details)
            logger.info(f"🎯 场景抽取: {scenario.get('role', '?')} / {scenario.get('pain', '?')}")

            # ✅ 2. 生成实战文
            article = self.generate_article(details, scenario=scenario)
            if not article:
                return {"status": "error", "error": "文章生成失败"}

            work_dir = Path(self.config["output_dir"]) / "tmp" / datetime.now().strftime("%Y%m%d_%H%M%S")
            assets_dir = work_dir / "assets"
            assets_dir.mkdir(parents=True, exist_ok=True)

            # ✅ 3. 生成插图
            illustration_paths: List[Path] = []
            try:
                prompts = self._generate_illustration_prompts(
                    details, article, count=self.config["illustration_count"],
                )
                if prompts:
                    illustration_paths = self._generate_illustrations(prompts, assets_dir)
            except Exception as e:
                logger.warning(f"⚠️ 插图流程失败，继续无图文章: {e}")

            if illustration_paths:
                article = self._insert_illustrations(article, illustration_paths)

            md_file = work_dir / "article.md"
            md_file.write_text(article, encoding="utf-8")

            illustration_str_paths = [str(p) for p in illustration_paths]
            cover = illustration_paths[0] if illustration_paths else None
            
            # ✅ 4. 发布草稿箱
            published = self.publish_to_wechat(
                article_md=article,
                repo_info=details,
                cover_image=cover,
                work_dir=work_dir,
            )

            history = self._load_history()
            if full_name not in history:
                history.append(full_name)
                self._save_history(history)

            elapsed = time.time() - start_time
            return {
                "status": "success" if published else "partial_success",
                "result": {
                    "repo": full_name,
                    "repo_url": details.get("html_url"),
                    "article_path": str(md_file),
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