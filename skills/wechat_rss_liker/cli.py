# skills/wechat_rss_liker/cli.py
import argparse
import sys
import json
from pathlib import Path

# 确保能导入 skill
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from skills.wechat_rss_liker.skill import WechatRssLiker

def main():
    parser = argparse.ArgumentParser(description="微信公众号 RSS 自动访问/点赞工具")
    parser.add_argument("--rss-file", type=str, required=True, help="包含 RSS 链接的 txt 或 json 文件路径")
    parser.add_argument("--mode", choices=["visit", "like"], default="visit", 
                        help="visit=仅访问滚动(刷活跃度), like=尝试点击赞(需微信扫码)")
    parser.add_argument("--hours", type=int, default=24, help="只处理最近 N 小时内的文章 (默认 24)")
    
    args = parser.parse_args()

    rss_file = Path(args.rss_file)
    if not rss_file.exists():
        print(f"❌ 文件不存在: {rss_file}")
        return

    # 支持 txt (每行一个链接) 或 json (列表)
    if rss_file.suffix == ".json":
        with open(rss_file, "r", encoding="utf-8") as f:
            rss_urls = json.load(f)
    else:
        with open(rss_file, "r", encoding="utf-8") as f:
            rss_urls = [line.strip() for line in f if line.strip().startswith("http")]

    if not rss_urls:
        print("⚠️ 未找到有效的 RSS 链接")
        return

    print(f"📡 加载了 {len(rss_urls)} 个 RSS 源")
    print(f"🎯 模式: {args.mode} | 时间窗口: 最近 {args.hours} 小时")
    print("-" * 50)

    liker = WechatRssLiker(rss_urls=rss_urls, mode=args.mode, max_age_hours=args.hours)
    liker.process_articles()

if __name__ == "__main__":
    main()