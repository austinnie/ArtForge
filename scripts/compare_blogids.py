# -*- coding: utf-8 -*-
"""对比 QQ空间 HTML 里的 blogid 和 posts.json 里已抓到的"""
import re, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS = ROOT / "output" / "posts.json"

# 已抓到的
d = json.loads(POSTS.read_text(encoding="utf-8"))
have = set(str(x["blogid"]) for x in d)
print(f"posts.json 里已抓：{len(have)} 个\n")

# 扫描 output 目录下所有 dump html
dumps = list((ROOT / "output").glob("qq_bloglist_dump*.html"))
if not dumps:
    print("❌ 没找到 qq_bloglist_dump*.html 文件")
    exit()

all_ids = set()
for f in dumps:
    text = f.read_text(encoding="utf-8", errors="ignore")
    ids = re.findall(r'/blog/(\d{8,})', text)
    ids += re.findall(r'blogid=(\d{8,})', text)
    ids = set(ids)
    print(f"{f.name}: 找到 {len(ids)} 个 blogid")
    all_ids |= ids

print(f"\nHTML 里总共：{len(all_ids)} 个 blogid")

missing = all_ids - have
print(f"❗ 漏抓的：{len(missing)} 个")
if missing:
    print("前 30 个漏的 blogid:")
    for m in sorted(missing, key=int)[:30]:
        print(f"  {m}")