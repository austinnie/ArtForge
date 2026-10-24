#!/usr/bin/env python
"""GitHub 仓库每日推荐 CLI（适配 skill v1.3.0）"""

import sys
import argparse
from pathlib import Path

project_root = Path(__file__).parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from skills.github_repo_daily import GitHubRepoDaily


def main():
    parser = argparse.ArgumentParser(description="GitHub 仓库每日推荐")
    parser.add_argument("--no-publish", action="store_true", help="不发布到微信公众号")
    parser.add_argument(
        "--theme", default=None,
        help="微信排版主题（不传则按仓库类型自动选：devtool/infra/library→github, app→magazine, tutorial→newspaper）",
    )
    parser.add_argument(
        "--backends", default=None,
        help="覆盖 LLM 后端优先级，逗号分隔（如 agnes,ollama）。不传则走 LLM_BACKENDS / GH_DAILY_LLM_BACKENDS",
    )
    args = parser.parse_args()

    config = {
        "wechat_publish": not args.no_publish,
        # ✅ 不传 --theme 时保持 None，让 skill 里的 THEME_BY_KIND 生效
        "wechat_theme": args.theme,
    }
    if args.backends:
        config["llm_backends"] = [b.strip() for b in args.backends.split(",") if b.strip()]

    skill = GitHubRepoDaily(config)
    result = skill.execute()

    if result["status"] == "success":
        r = result["result"]
        print(f"✅ 推荐仓库: {r['repo']}")
        print(f"🏷️  类型    : {r.get('repo_kind', '-')}")
        print(f"🎨 主题    : {r.get('theme', '-')}")
        print(f"📄 文章    : {r['article_path']}")
        print(f"🖼️  配图    : {len(r.get('illustrations', []))} 张")
        print(f"📤 已发布  : {r['published']}")
        print(f"⏱️  耗时    : {r.get('elapsed', '-')}")
    else:
        print(f"❌ 失败: {result.get('error')}")


if __name__ == "__main__":
    main()