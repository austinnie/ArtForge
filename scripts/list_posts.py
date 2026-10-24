# -*- coding: utf-8 -*-
"""列出 posts.json 里所有日志的编号 / blogid / 标题"""
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
POSTS = PROJECT_ROOT / "output" / "posts.json"

d = json.loads(POSTS.read_text(encoding="utf-8"))
print(f"共 {len(d)} 篇\n")
for i, x in enumerate(d, 1):
    bid = x.get("blogid", "")
    title = x.get("title", "")
    print(f"{i:3d} | {bid} | {title[:60]}")