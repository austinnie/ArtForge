# -*- coding: utf-8 -*-
"""
每天定时从 posts.json 里挑一篇未推送的日志，创建微信草稿。
- 按顺序从头到尾发（可以改成随机）
- 记录已推送的 blogid，避免重复
- 兼容 qq_to_wechat.py 里的 WeChatAPI 和图片处理逻辑
"""
import os
import re
import sys
import json
import time
import random
import argparse
from pathlib import Path

# 让 daily_push.py 能 import qq_to_wechat 里的函数/类
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from qq_to_wechat import (  # noqa: E402
    WeChatAPI, POSTS_JSON, WECHAT_APP_ID, WECHAT_APP_SECRET,
    THUMB_MEDIA_ID, IMG_CACHE,
)
import requests  # noqa: E402

PROJECT_ROOT = SCRIPT_DIR.parent
HISTORY_FILE = PROJECT_ROOT / "output" / "pushed_history.json"


def load_history():
    if HISTORY_FILE.exists():
        return set(json.loads(HISTORY_FILE.read_text(encoding="utf-8")))
    return set()


def save_history(pushed: set):
    HISTORY_FILE.write_text(
        json.dumps(sorted(pushed), ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def pick_one(posts, pushed, mode="order"):
    """挑一篇还没推送的"""
    remaining = [p for p in posts if str(p.get("blogid")) not in pushed]
    if not remaining:
        return None
    if mode == "random":
        return random.choice(remaining)
    return remaining[0]


def process_images_direct(html: str, wx: WeChatAPI, referer: str):
    """复制 qq_to_wechat.py 里图片处理逻辑（避免循环导入）"""
    IMG_RE = re.compile(r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>', re.I)

    def repl(m):
        src = m.group(1)
        if src.startswith("data:"):
            return ""
        if "mmbiz.qpic.cn" in src:
            return m.group(0)

        # 外链下载 → 上传微信
        try:
            import hashlib, mimetypes
            h = hashlib.md5(src.encode("utf-8")).hexdigest()
            ext = os.path.splitext(src.split("?")[0])[1].lower()
            if ext not in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
                ext = ".jpg"
            path = IMG_CACHE / f"{h}{ext}"
            if not (path.exists() and path.stat().st_size > 0):
                r = requests.get(src, headers={"User-Agent": "Mozilla/5.0",
                                               "Referer": referer}, timeout=30)
                if r.status_code != 200 or len(r.content) < 200:
                    return m.group(0)
                path.write_bytes(r.content)

            new_url = wx.upload_content_image(path)
            if new_url:
                print(f"      🖼️  上传成功: {src[:40]}…")
                return f'<img src="{new_url}" />'
        except Exception as e:
            print(f"      ⚠️ 图片处理失败: {e}")
        return m.group(0)

    return IMG_RE.sub(repl, html)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["order", "random"], default="order",
                    help="推送顺序：order=按列表顺序 / random=随机")
    ap.add_argument("--count", type=int, default=1,
                    help="每天推送几篇（默认1）")
    ap.add_argument("--dry-run", action="store_true",
                    help="只打印，不真发")
    args = ap.parse_args()

    print("=" * 60)
    print(f"📅 每日推送 ({time.strftime('%Y-%m-%d %H:%M:%S')})")
    print("=" * 60)

    if not POSTS_JSON.exists():
        print(f"❌ 找不到 {POSTS_JSON}")
        return 1

    posts = json.loads(POSTS_JSON.read_text(encoding="utf-8"))
    pushed = load_history()
    print(f"📚 总篇数: {len(posts)}")
    print(f"✅ 已推送: {len(pushed)}")
    print(f"📌 剩余: {len(posts) - len(pushed)}")
    print(f"🎯 顺序: {args.mode} | 每天: {args.count} 篇")
    print()

    wx = None
    if not args.dry_run:
        wx = WeChatAPI(WECHAT_APP_ID, WECHAT_APP_SECRET)
        if not wx.get_access_token():
            print("❌ 微信登录失败")
            return 2

    ok_count = 0
    for n in range(args.count):
        post = pick_one(posts, pushed, args.mode)
        if post is None:
            print("🎉 所有日志都推完了！")
            break

        bid = str(post.get("blogid"))
        title = post.get("title") or f"日志_{bid}"
        print(f"[{n+1}/{args.count}] {title[:50]}  (blogid={bid})")

        html = post.get("content", "")
        if not args.dry_run:
            html = process_images_direct(html, wx, post.get("url", ""))
            if wx.add_draft(title, html):
                pushed.add(bid)
                save_history(pushed)
                ok_count += 1
                print(f"      ✅ 已创建草稿，标记 blogid={bid}")
            else:
                print(f"      ❌ 创建失败，未标记")
        else:
            print("      (dry-run 不发)")

        if n < args.count - 1:
            time.sleep(2)

    print(f"\n🎉 完成：{ok_count}/{args.count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())