# skills/wechat_liker/cli.py
import argparse
import sys
from pathlib import Path

# 确保能导入 skill (兼容从任何目录调用此脚本)
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from skills.wechat_liker.skill import WechatLiker


def main():
    parser = argparse.ArgumentParser(description="微信公众号文章自动点赞工具")
    parser.add_argument("--file", type=str, help="包含文章链接的 txt 文件路径（每行一个链接）")
    parser.add_argument("--url", type=str, help="单篇文章链接")
    parser.add_argument("--action", choices=["like", "wow"], default="like", 
                        help="like=赞/推荐, wow=在看 (默认 like)")
    parser.add_argument("--min-delay", type=int, default=10, help="最小休眠秒数")
    parser.add_argument("--max-delay", type=int, default=20, help="最大休眠秒数")
    
    args = parser.parse_args()

    if not args.file and not args.url:
        print("❌ 请提供 --file 或 --url")
        return

    liker = WechatLiker(delay_range=(args.min_delay, args.max_delay))
    
    urls = []
    if args.url:
        urls.append(args.url)
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            urls.extend([line.strip() for line in f if line.strip().startswith("http")])

    if not urls:
        print("⚠️ 未找到有效的链接")
        return

    liker.batch_like(urls, action=args.action)


if __name__ == "__main__":
    main()