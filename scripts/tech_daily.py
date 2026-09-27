# scripts/tech_daily.py
"""
技术热点日更：RSS → 文章 + 配图 → 排版 → 推公众号

用法：
  python scripts/tech_daily.py
  python scripts/tech_daily.py --category tech --style "深度技术型" ^
    --theme newspaper --publish
  python scripts/tech_daily.py --no-publish
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from dotenv import load_dotenv
    _env = PROJECT_ROOT / ".env"
    load_dotenv(_env if _env.exists() else None)
except ImportError:
    pass


def section(t: str):
    print()
    print("=" * 72)
    print(f"  {t}")
    print("=" * 72)


def step_news(category: str) -> str:
    """步骤 1：抓新闻，生成简报文本"""
    section("步骤 1/4：抓技术热点")
    from skills.news_aggregator import NewsAggregator

    agg = NewsAggregator()
    r = agg.execute(category=category, top_n=15)
    if r.get("status") != "success":
        print(f"❌ 抓取失败: {r.get('error')}")
        return ""
    report = r["result"].get("report", "")
    print(f"✅ 抓取到 {r['result'].get('unique_count', 0)} 条")
    return report


def step_article(category: str, style: str, report: str) -> Path | None:
    """步骤 2：用 tech_hot_article 写文章"""
    section("步骤 2/4：AI 写文章 + 配图")
    from skills.tech_hot_article import TechHotArticle

    gen = TechHotArticle()
    r = gen.execute(style=style, hot_index=None)
    if r.get("status") != "success":
        print(f"❌ 文章生成失败: {r.get('error')}")
        return None

    word_file = r["result"].get("word_file")
    article_json = r["result"].get("article_file")

    print(f"✅ 标题: {r['result'].get('title')}")
    print(f"   Word: {word_file}")
    print(f"   JSON: {article_json}")

    # tech_hot_article 写的是 docx，不是 md
    # 需要转成 md 才能给 wechat_formatter
    # 这里直接读它的 article JSON 里的 body 字段写一个 md
    import json
    data = json.loads(Path(article_json).read_text(encoding="utf-8"))
    article = data["article"]
    md_path = Path(article_json).with_suffix(".md")
    md_path.write_text(
        f"# {article['title']}\n\n{article['body']}\n",
        encoding="utf-8")
    print(f"   MD:   {md_path}")
    return md_path


def step_format(md_path: Path, theme: str,
                footer_image: str | None = None) -> Path | None:
    section("步骤 3/4：微信排版")
    from skills.wechat_formatter import WechatFormatter
    fmt = WechatFormatter()
    kwargs = {"theme": theme, "open": False}
    if footer_image:
        fp = Path(footer_image)
        if not fp.is_absolute():
            fp = PROJECT_ROOT / fp
        if fp.exists():
            kwargs["footer_image"] = str(fp)
    r = fmt.format(str(md_path), **kwargs)
    if r.get("status") != "success":
        print(f"❌ 排版失败: {r.get('error')}")
        return None
    art_dir = Path(r["result"]["article_dir"])
    print(f"✅ 排版: {art_dir}")
    return art_dir


def step_publish(article_dir: Path):
    section("步骤 4/4：推公众号草稿")
    from skills.wechat_formatter import WechatFormatter
    r = WechatFormatter().publish(str(article_dir))
    if r.get("status") == "success":
        print("✅ 已推送")
    else:
        print(f"❌ 推送失败: {r.get('error')}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--category", default="tech",
                    choices=["tech", "business", "world",
                             "china", "usa", "japan", "korea"])
    ap.add_argument("--style", default="专业分析型",
                    choices=["专业分析型", "通俗科普型", "深度技术型",
                             "行业观察型", "趋势预测型"])
    ap.add_argument("--theme", default="bytedance")
    ap.add_argument("--footer-image", default=None)
    ap.add_argument("--publish", action="store_true")
    args = ap.parse_args()

    # 1. 抓新闻
    report = step_news(args.category)

    # 2. 文章
    md = step_article(args.category, args.style, report)
    if not md:
        sys.exit(1)

    # 3. 排版
    art_dir = step_format(md, args.theme, args.footer_image)
    if not art_dir:
        sys.exit(1)

    # 4. 推送
    if args.publish:
        step_publish(art_dir)
    else:
        section("步骤 4/4：跳过推送")
        print(f"   预览: {art_dir / 'preview.html'}")


if __name__ == "__main__":
    main()