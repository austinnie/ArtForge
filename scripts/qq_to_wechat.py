#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QQ空间日志 -> 微信公众号草稿箱 一体化工具

流程：
1. 从 QQ_START_BLOGID 开始，用 blog_get_specialtitle 接口翻页拿全部 blogId
2. 对每个 blogId 调 blog_output_data 拿标题/日期/正文 HTML
3. 正文中的外链图下载 → 上传微信素材库 → 替换为微信CDN
4. 调微信 draft/add 创建草稿

用法：
    python scripts/qq_to_wechat.py --fetch         # 只抓取，生成 posts.json
    python scripts/qq_to_wechat.py --dry-run       # 抓取+预览，不发草稿
    python scripts/qq_to_wechat.py --limit 5       # 发前5篇到草稿箱
    python scripts/qq_to_wechat.py --skip-fetch    # 跳过抓取，直接用 posts.json
    python scripts/qq_to_wechat.py                 # 全量：抓取+发草稿
"""
import os, re, sys, json, time, argparse, mimetypes, hashlib
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# ============================================================
# 0. 路径 & 环境
# ============================================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"

if not ENV_PATH.exists():
    print(f"❌ 未找到 .env: {ENV_PATH}"); sys.exit(1)
load_dotenv(ENV_PATH)
print(f"✅ 已加载: {ENV_PATH}")

WECHAT_APP_ID     = os.getenv("WECHAT_APP_ID", "").strip()
WECHAT_APP_SECRET = os.getenv("WECHAT_APP_SECRET", "").strip()
THUMB_MEDIA_ID    = os.getenv("WECHAT_THUMB_MEDIA_ID", "").strip()

QQ_UIN            = os.getenv("QQ_UIN", "").strip()
QQ_START_BLOGID   = os.getenv("QQ_START_BLOGID", "").strip()
QQ_COOKIE         = os.getenv("QQ_COOKIE", "").strip()
QQ_G_TK           = os.getenv("QQ_G_TK", "").strip()

POSTS_JSON        = PROJECT_ROOT / "output" / "posts.json"
IMG_CACHE         = PROJECT_ROOT / "output" / "imgs_cache"
POSTS_JSON.parent.mkdir(parents=True, exist_ok=True)
IMG_CACHE.mkdir(parents=True, exist_ok=True)

if not WECHAT_APP_ID or not WECHAT_APP_SECRET:
    print("❌ 缺 WECHAT_APP_ID / WECHAT_APP_SECRET"); sys.exit(1)

# ============================================================
# 1. 微信 API
# ============================================================
class WeChatAPI:
    def __init__(self, appid, secret):
        self.appid, self.secret = appid, secret
        self.access_token, self.token_expires = None, 0

    def get_access_token(self):
        if self.access_token and time.time() < self.token_expires:
            return self.access_token
        url = "https://api.weixin.qq.com/cgi-bin/token"
        p = {"grant_type": "client_credential",
             "appid": self.appid, "secret": self.secret}
        try:
            r = requests.get(url, params=p, timeout=15).json()
        except Exception as e:
            print(f"❌ Token 异常: {e}"); return None
        if "access_token" in r:
            self.access_token = r["access_token"]
            self.token_expires = time.time() + r["expires_in"] - 300
            print("✅ 微信 Token 获取成功"); return self.access_token
        print(f"❌ Token 失败: {r}"); return None

    def upload_content_image(self, image_path: Path):
        token = self.get_access_token()
        if not token: return None
        url = f"https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token={token}"
        mime = mimetypes.guess_type(str(image_path))[0] or "image/jpeg"
        try:
            with open(image_path, "rb") as f:
                r = requests.post(url, files={"media": (image_path.name, f, mime)},
                                  timeout=60).json()
        except Exception as e:
            print(f"      ⚠️ 上传图异常: {e}"); return None
        if "url" in r: return r["url"]
        print(f"      ⚠️ 上传图失败: {r}"); return None

    def add_draft(self, title, content_html):
        token = self.get_access_token()
        if not token: return False
        url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}"
        plain = re.sub(r"<[^>]+>", "", content_html)
        plain = re.sub(r"\s+", " ", plain).strip()
        digest = plain[:100] + ("..." if len(plain) > 100 else "")
        art = {"title": (title or "无标题")[:64], "author": "",
               "digest": digest, "content": content_html,
               "content_source_url": "", "need_open_comment": 0,
               "only_fans_can_comment": 0}
        if THUMB_MEDIA_ID: art["thumb_media_id"] = THUMB_MEDIA_ID
        try:
            r = requests.post(url, json={"articles": [art]}, timeout=30).json()
        except Exception as e:
            print(f"      ❌ 请求异常: {e}"); return False
        # 成功：微信返回 media_id，不返回 errcode
        if "media_id" in r:
            print(f"      ✅ 草稿创建成功 (media_id: {r['media_id'][:20]}...)")
            return True
        if r.get("errcode") == 0:
            print("      ✅ 草稿创建成功")
            return True
        print(f"      ❌ 创建失败: {r}")
        return False


# ============================================================
# 2. QQ空间日志抓取
# ============================================================
class QzoneBlogFetcher:
    SPECIAL_API  = "https://user.qzone.qq.com/proxy/domain/b.qzone.qq.com/cgi-bin/blognew/blog_get_specialtitle"
    DETAIL_API   = "https://user.qzone.qq.com/proxy/domain/b.qzone.qq.com/cgi-bin/blognew/blog_output_data"
    BLOG_URL_TPL = "https://user.qzone.qq.com/{uin}/blog/{bid}"

    def __init__(self, uin, cookie, g_tk):
        self.uin, self.cookie, self.g_tk = uin, cookie, g_tk
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/122.0.0.0 Safari/537.36",
            "Cookie": cookie,
            "Referer": f"https://user.qzone.qq.com/{uin}/2",
            "Accept-Language": "zh-CN,zh;q=0.9",
        }

    # ---------- 2.1 从起点向后翻，拿全部 blogId ----------
    def fetch_all_blogids(self, start_blogid: str,
                          max_rounds: int = 200):
        """
        接口每次返回 next_list（通常 5 篇），
        取最后一个 blogid 作新基准，继续向后翻。
        """
        print(f"\n📋 从 blogid={start_blogid} 开始向后翻页...")
        ordered = [start_blogid]
        seen = {start_blogid}
        cursor = start_blogid

        for rnd in range(1, max_rounds + 1):
            ids = self._call_special(cursor)
            new_ids = [b for b in ids if b not in seen]
            if not new_ids:
                print(f"  第{rnd}轮：无新数据，结束（累计 {len(ordered)} 篇）")
                break

            for b in new_ids:
                seen.add(b)
                ordered.append(b)
            print(f"  第{rnd}轮：+{len(new_ids)}（累计 {len(ordered)}）")

            cursor = new_ids[-1]
            time.sleep(0.35)

        # 再从起点向前翻（prev_list），以防漏了更新的日志
        cursor = start_blogid
        for rnd in range(1, max_rounds + 1):
            ids = self._call_special(cursor, direction="prev")
            new_ids = [b for b in ids if b not in seen]
            if not new_ids:
                print(f"  向前第{rnd}轮：无新数据，结束")
                break
            # 向前的结果要插到最前面（保持时间顺序）
            for b in new_ids:
                seen.add(b)
            ordered = new_ids + ordered
            print(f"  向前第{rnd}轮：+{len(new_ids)}（累计 {len(ordered)}）")
            cursor = new_ids[0]
            time.sleep(0.35)

        print(f"✅ 共拿到 {len(ordered)} 个 blogId")
        return ordered

    def _call_special(self, blogid, direction="next"):
        """
        direction=next → 用 nextnum=1 拉后面
        direction=prev → 用 prevnum=1 拉前面
        注意：接口限制，nextnum/prevnum 最小值是 1（实际返回 5 篇）
        """
        params = {
            "uin": self.uin, "blogid": blogid,
            "category": "", "catehex": "",
            "sorttype": "0", "fupdate": "1", "iNotice": "0",
            "inCharset": "utf-8", "outCharset": "utf-8",
            "format": "jsonp", "ref": "qzone",
            "g_tk": self.g_tk,
        }
        if direction == "next":
            params["nextnum"] = "1"
        else:
            params["prevnum"] = "1"

        try:
            r = requests.get(self.SPECIAL_API, params=params,
                             headers=self.headers, timeout=20)
            r.encoding = "utf-8"
            text = r.text.strip()
        except Exception as e:
            print(f"    ⚠️ special 接口异常: {e}")
            return []

        m = re.search(r"\{.*\}", text, re.S)
        if not m:
            return []
        try:
            data = json.loads(m.group(0))
        except Exception:
            return []

        if data.get("code") != 0:
            print(f"    ⚠️ 接口返回: {data.get('message')}")
            return []

        d = data.get("data") or {}
        key = "next_list" if direction == "next" else "prev_list"
        items = d.get(key) or []

        ids = []
        for it in items:
            if isinstance(it, dict):
                bid = it.get("blogid") or it.get("blogId") or it.get("id")
                if bid:
                    ids.append(str(bid))
        return ids

    # ---------- 2.2 抓单篇详情 ----------
    def fetch_blog_detail(self, blogid):
        params = {
            "uin": self.uin, "blogid": blogid,
            "styledm": "qzonestyle.gtimg.cn", "imgdm": "qzs.qq.com",
            "bdm": "b.qzone.qq.com", "mode": "2",
            "numperpage": "15", "dprefix": "",
            "inCharset": "gb2312", "outCharset": "gb2312",
            "ref": "qzone", "page": "1",
        }
        try:
            r = requests.get(self.DETAIL_API, params=params,
                             headers=self.headers, timeout=20)
            r.encoding = "gb2312"
            html = r.text
        except Exception as e:
            return {"title": "", "content": "", "_error": str(e)}

        soup = BeautifulSoup(html, "html.parser")
        # 优先用可靠的正文标题容器，其次 <h1>，最后 <title>
        title_el = (soup.find(id="blogTitle") or
                    soup.find(class_="blog_title") or
                    soup.find("h1"))
        title = title_el.get_text(strip=True) if title_el else ""

        # 兜底：从 <title> 里切出干净标题
        if not title:
            t = soup.find("title")
            if t:
                title = t.get_text(strip=True)
        # 清洗：去掉尾部的"编辑于"、"-QQ空间"、"阅读(N)" 等噪声
        title = re.sub(r"(编辑于|编辑|发表于).*$", "", title).strip()
        title = re.sub(r"[-—_|\s]*QQ空间.*$", "", title).strip()
        title = re.sub(r"阅读\s*\(\s*\d+\s*\)", "", title).strip()
        title = title[:64].strip() or "无标题"

        body = None
        for sel in ({"id": "blogDetailDiv"}, {"class_": "blog-detail"},
                    {"class_": "blog-content"}, {"class_": "blog_content"},
                    {"id": "content"}, {"class_": "content"}):
            body = soup.find(**sel)
            if body:
                break
        if not body:
            body = soup.body

        return {"title": title, "content": self._clean_body(body),
                "url": self.BLOG_URL_TPL.format(uin=self.uin, bid=blogid)}

    def _clean_body(self, body):
        if body is None:
            return ""
        soup = BeautifulSoup(str(body), "html.parser")
        for t in soup(["script", "style", "noscript", "button",
                       "input", "iframe", "ins"]):
            t.decompose()
        for cls in ("comment", "ad", "share", "report", "fav",
                    "vote", "toolbar", "blog_tag", "blog-foot"):
            for t in soup.find_all(class_=re.compile(cls)):
                t.decompose()

        for img in soup.find_all("img"):
            src = (img.get("src") or img.get("orisrc") or
                   img.get("data-src") or "")
            if not src:
                img.decompose()
                continue
            img["src"] = src
            for a in ("onclick", "onload", "class", "id", "style"):
                if img.has_attr(a):
                    del img[a]

        paragraphs = []
        for el in soup.find_all(["p", "div", "section"]):
            txt = el.get_text(" ", strip=True)
            if txt and len(txt) > 1:
                paragraphs.append(txt)

        # 去掉段落里的重复（同一个 div 的祖先/子节点会重复抓到）
        seen_txt = set()
        uniq_paras = []
        for p in paragraphs:
            # 跳过跟标题完全一致的首行（正文常见的"标题重复"现象）
            if p.strip() in seen_txt:
                continue
            seen_txt.add(p.strip())
            uniq_paras.append(p)
        paragraphs = uniq_paras

        imgs = [i["src"] for i in soup.find_all("img") if i.get("src")]

        parts = [f"<p>{p}</p>" for p in paragraphs]
        parts += [f'<p><img src="{u}" /></p>' for u in imgs]
        if parts:
            return "\n".join(parts)
        return re.sub(r"\s+", " ", soup.get_text(" ", strip=True))

# ============================================================
# 3. 图片处理
# ============================================================
IMG_RE = re.compile(r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>', re.I)

def download_image(url: str, referer: str):
    try:
        h = hashlib.md5(url.encode("utf-8")).hexdigest()
        ext = os.path.splitext(url.split("?")[0])[1].lower()
        if ext not in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
            ext = ".jpg"
        path = IMG_CACHE / f"{h}{ext}"
        if path.exists() and path.stat().st_size > 0:
            return path
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0",
                                       "Referer": referer}, timeout=30)
        if r.status_code != 200 or len(r.content) < 200:
            return None
        path.write_bytes(r.content)
        return path
    except Exception as e:
        print(f"      ⚠️ 下载图失败: {e}"); return None

def process_images(html: str, wx, referer: str, dry: bool):
    def repl(m):
        src = m.group(1)
        if src.startswith("data:"): return ""
        if "mmbiz.qpic.cn" in src: return m.group(0)
        path = download_image(src, referer)
        if not path: return m.group(0)
        if dry:
            print(f"      🖼️  (dry-run) {src[:60]}"); return m.group(0)
        new_url = wx.upload_content_image(path)
        if new_url:
            print(f"      🖼️  {src[:40]}… -> {new_url[:50]}…")
            return f'<img src="{new_url}" />'
        return m.group(0)
    return IMG_RE.sub(repl, html)


# ============================================================
# 4. 主流程
# ============================================================
def cmd_fetch(args):
    if not QQ_UIN or not QQ_COOKIE or not QQ_START_BLOGID:
        print("❌ .env 里缺 QQ_UIN / QQ_COOKIE / QQ_START_BLOGID")
        return False

    # ========= 多锚点：从多个起点分别翻页，合并去重 =========
    starts = [QQ_START_BLOGID.strip()]

    # 从 .env 读追加锚点，逗号分隔
    extra = (os.getenv("QQ_EXTRA_STARTS", "") or "").strip()
    if extra:
        extra_list = [s.strip() for s in extra.split(",") if s.strip()]
        starts += extra_list

    # 去重（防止 .env 里重复写）
    seen_starts = set()
    starts_uniq = []
    for s in starts:
        if s and s not in seen_starts:
            seen_starts.add(s)
            starts_uniq.append(s)
    starts = starts_uniq

    print(f"\n📋 共 {len(starts)} 个锚点：")
    for i, s in enumerate(starts, 1):
        print(f"   {i}. {s}")

    fetcher = QzoneBlogFetcher(QQ_UIN, QQ_COOKIE, QQ_G_TK)

    all_ids = []
    seen_ids = set()
    for i, st in enumerate(starts, 1):
        print(f"\n===== 锚点 {i}/{len(starts)}: blogid={st} =====")
        try:
            ids = fetcher.fetch_all_blogids(st)
        except Exception as e:
            print(f"   ❌ 抓取异常: {e}")
            continue
        new = [x for x in ids if x not in seen_ids]
        for x in new:
            seen_ids.add(x)
            all_ids.append(x)
        print(f"   ✅ 新增 {len(new)}，累计 {len(all_ids)}")

    if not all_ids:
        print("❌ 没拿到 blogId")
        return False

    # 按 blogid 降序（最新的在前）
    all_ids = sorted(set(all_ids), key=lambda x: int(x), reverse=True)
    print(f"\n✅ 去重排序后共 {len(all_ids)} 个 blogId")

    print(f"\n📥 开始抓正文（共 {len(all_ids)} 篇）...")
    posts = []
    for i, bid in enumerate(all_ids, 1):
        print(f"[{i}/{len(all_ids)}] blogid={bid}")
        d = fetcher.fetch_blog_detail(bid)
        if d.get("_error"):
            print(f"   ❌ {d['_error']}")
            continue
        if len(re.sub(r"<[^>]+>", "", d["content"])) < 10:
            print("   ⚠️ 正文过短，跳过")
            continue
        posts.append({
            "title": d["title"],
            "content": d["content"],
            "url": d["url"],
            "blogid": bid,
        })
        time.sleep(0.35)

    POSTS_JSON.write_text(
        json.dumps(posts, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"\n✅ 写出 {POSTS_JSON}（{len(posts)} 篇）")
    return True

def cmd_publish(args):
    if not POSTS_JSON.exists():
        print(f"❌ 找不到 {POSTS_JSON}"); return False
    posts = json.loads(POSTS_JSON.read_text(encoding="utf-8"))

    # ---- 按 --ids 过滤（1-based 序号）----
    if getattr(args, "ids", ""):
        want = []
        for s in args.ids.split(","):
            s = s.strip()
            if s.isdigit():
                want.append(int(s))
        picked = []
        for i in want:
            if 1 <= i <= len(posts):
                picked.append(posts[i-1])
            else:
                print(f"⚠️ 序号 {i} 超出范围（共 {len(posts)} 篇），跳过")
        posts = picked
        print(f"🎯 按序号选取：{want} → 命中 {len(posts)} 篇")

    # ---- 按 --blogids 过滤 ----
    if getattr(args, "blogids", ""):
        want = set(s.strip() for s in args.blogids.split(",") if s.strip())
        posts = [p for p in posts if str(p.get("blogid")) in want]
        print(f"🎯 按 blogid 选取 → 命中 {len(posts)} 篇")

    # ---- 按 --from / --to 过滤 ----
    if getattr(args, "range_from", 0) or getattr(args, "range_to", 0):
        f = args.range_from if args.range_from > 0 else 1
        t = args.range_to if args.range_to > 0 else len(posts)
        posts = posts[f-1:t]
        print(f"🎯 按序号范围 [{f}, {t}] → {len(posts)} 篇")

    if args.limit > 0:
        posts = posts[:args.limit]
    if not posts:
        print("❌ 过滤后没有内容")
        return False
    print(f"\n📤 待发 {len(posts)} 篇")

    wx = WeChatAPI(WECHAT_APP_ID, WECHAT_APP_SECRET)
    if not args.dry_run and not wx.get_access_token():
        print("❌ 微信登录失败"); return False

    ok = 0
    for i, p in enumerate(posts, 1):
        title = p.get("title") or f"日志_{i}"
        print(f"\n[{i}/{len(posts)}] {title[:40]}")
        html = process_images(p.get("content", ""), wx,
                              p.get("url", ""), args.dry_run)
        if args.dry_run:
            print("      (dry-run 不发)"); ok += 1; continue
        if wx.add_draft(title, html): ok += 1
        time.sleep(1.5)
    print(f"\n🎉 完成：{ok}/{len(posts)}")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true", help="只抓取")
    ap.add_argument("--dry-run", action="store_true", help="预览不发")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--skip-fetch", action="store_true", help="跳过抓取")
    ap.add_argument("--ids", type=str, default="",
                    help="按序号发（1-based），逗号分隔，例如 --ids 1,3,5,10")
    ap.add_argument("--blogids", type=str, default="",
                    help="按 blogid 发，逗号分隔")
    ap.add_argument("--from", dest="range_from", type=int, default=0,
                    help="起始序号（含）")
    ap.add_argument("--to", dest="range_to", type=int, default=0,
                    help="结束序号（含）")
    args = ap.parse_args()

    print("=" * 60)
    print("🚀 QQ空间日志 -> 微信公众号草稿箱")
    print("=" * 60)

    if not args.skip_fetch:
        if not cmd_fetch(args): return
    if args.fetch: return
    cmd_publish(args)


if __name__ == "__main__":
    main()
