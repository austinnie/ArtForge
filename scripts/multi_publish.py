# scripts/multi_publish.py
"""
多平台分发：一次生成，分发到 13 个平台

支持平台（来自 social_auto_upload）：
  视频：抖音、快手、小红书、B站、视频号、YouTube、微博、虎扑、百家号、支付宝
  图文：抖音、快手、小红书

用法：
  # 图文分发
  python scripts/multi_publish.py note ^
    --images output/tang/*.png ^
    --title "唐风 · 敦煌飞天" ^
    --note "这次整理了 6 张敦煌飞天..." ^
    --tags 敦煌,国风,AI绘画 ^
    --platforms xiaohongshu,douyin,kuaishou

  # 视频分发
  python scripts/multi_publish.py video ^
    --file output/videos/xxx.mp4 ^
    --title "敦煌飞天" ^
    --desc "4K 视频，全程 AI 生成" ^
    --platforms tencent,bilibili,youtube

  # 批量：把目录里的视频分发到 B站/视频号
  python scripts/multi_publish.py video ^
    --file output/videos/xxx.mp4 ^
    --title "test" --platforms tencent,bilibili
"""
from __future__ import annotations

import argparse
import glob
import sys
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


VIDEO_PLATFORMS = [
    "douyin", "kuaishou", "xiaohongshu", "bilibili",
    "tencent", "alipay", "weibo", "hupu", "youtube", "baijiahao",
]
NOTE_PLATFORMS = ["douyin", "kuaishou", "xiaohongshu"]


def section(t: str):
    print()
    print("=" * 72)
    print(f"  {t}")
    print("=" * 72)


def publish_note(images: list[str], title: str, note: str,
                 tags: list[str], platforms: list[str],
                 account: str = "test"):
    from skills.social_auto_upload import SocialAutoUpload
    pub = SocialAutoUpload()

    ok, fail = [], []
    for plat in platforms:
        if plat not in NOTE_PLATFORMS:
            print(f"⏭️  {plat} 不支持图文，跳过")
            continue
        print(f"\n📤 {plat} 图文…")
        try:
            r = pub.publish_note(
                platform=plat, images=images,
                title=title, note=note, tags=tags,
                account=account)
            if r.get("status") == "success":
                print(f"   ✅ {plat}")
                ok.append(plat)
            else:
                print(f"   ❌ {r.get('error')}")
                fail.append(plat)
        except Exception as e:
            print(f"   ❌ {e}")
            fail.append(plat)
    return ok, fail


def publish_video(file: str, title: str, desc: str,
                  tags: list[str], platforms: list[str],
                  account: str = "test",
                  thumbnail: str | None = None,
                  tid: int | None = None):
    from skills.social_auto_upload import SocialAutoUpload
    pub = SocialAutoUpload()

    ok, fail = [], []
    for plat in platforms:
        if plat not in VIDEO_PLATFORMS:
            print(f"⏭️  {plat} 不支持视频，跳过")
            continue
        print(f"\n📤 {plat} 视频…")
        try:
            kwargs = {
                "platform": plat, "file": file,
                "title": title, "desc": desc, "tags": tags,
                "account": account,
            }
            if thumbnail:
                kwargs["thumbnail"] = thumbnail
            if tid is not None and plat == "bilibili":
                kwargs["tid"] = tid
            r = pub.publish_video(**kwargs)
            if r.get("status") == "success":
                print(f"   ✅ {plat}")
                ok.append(plat)
            else:
                print(f"   ❌ {r.get('error')}")
                fail.append(plat)
        except Exception as e:
            print(f"   ❌ {e}")
            fail.append(plat)
    return ok, fail


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="command", required=True)

    # note 子命令
    pn = sub.add_parser("note", help="图文分发")
    pn.add_argument("--images", nargs="+", required=True)
    pn.add_argument("--title", required=True)
    pn.add_argument("--note", default="")
    pn.add_argument("--tags", default="")
    pn.add_argument("--platforms", default="xiaohongshu,douyin,kuaishou")
    pn.add_argument("--account", default="test")

    # video 子命令
    pv = sub.add_parser("video", help="视频分发")
    pv.add_argument("--file", required=True)
    pv.add_argument("--title", required=True)
    pv.add_argument("--desc", default="")
    pv.add_argument("--tags", default="")
    pv.add_argument("--platforms", default="tencent,bilibili")
    pv.add_argument("--account", default="test")
    pv.add_argument("--thumbnail", default=None)
    pv.add_argument("--tid", type=int, default=None)

    args = ap.parse_args()

    if args.command == "note":
        # 展开 glob
        imgs = []
        for pat in args.images:
            if any(c in pat for c in "*?["):
                imgs.extend(glob.glob(pat))
            else:
                imgs.append(pat)
        imgs = [str(Path(p).resolve()) for p in imgs
                if Path(p).exists()][:20]
        if not imgs:
            print("❌ 没有有效图片")
            sys.exit(1)

        platforms = [p.strip() for p in args.platforms.split(",") if p.strip()]
        tags = [t.strip() for t in args.tags.split(",") if t.strip()]

        section(f"图文分发 → {platforms}")
        ok, fail = publish_note(
            images=imgs, title=args.title, note=args.note,
            tags=tags, platforms=platforms, account=args.account)

        print(f"\n✅ 成功: {ok}")
        print(f"❌ 失败: {fail}")

    elif args.command == "video":
        file = str(Path(args.file).resolve())
        if not Path(file).exists():
            print(f"❌ 文件不存在: {file}")
            sys.exit(1)

        platforms = [p.strip() for p in args.platforms.split(",") if p.strip()]
        tags = [t.strip() for t in args.tags.split(",") if t.strip()]

        section(f"视频分发 → {platforms}")
        ok, fail = publish_video(
            file=file, title=args.title, desc=args.desc,
            tags=tags, platforms=platforms, account=args.account,
            thumbnail=args.thumbnail, tid=args.tid)

        print(f"\n✅ 成功: {ok}")
        print(f"❌ 失败: {fail}")


if __name__ == "__main__":
    main()