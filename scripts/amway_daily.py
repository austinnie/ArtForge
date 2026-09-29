#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
安利产品每日推送入口
源文件目录：output/amway_daily_work/single_products_sharebar
"""
import sys
import logging
from pathlib import Path

# 获取 ArtForge 项目根目录
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from skills.amway_daily.skill import AmwayDaily

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    
    # ✅ 修正：直接指向你截图里的源文件目录
    docx_dir = PROJECT_ROOT / "output" / "amway_daily_work" / "single_products_sharebar"
    
    # 生成的 Markdown 和提取的图片放在这里（避免污染源文件目录）
    work_dir = PROJECT_ROOT / "output" / "amway_daily_work" / "single_products_sharebar_md"
    
    # 队列记录文件
    queue_file = PROJECT_ROOT / "data" / "amway_queue_sharebar.json"
    
    print("=" * 60)
    print("   安利产品每日自动推送 (Sharebar版)")
    print("=" * 60)
    print(f"📂 源文件目录: {docx_dir}")
    print(f"📝 工作目录  : {work_dir}")
    print("=" * 60)
    
    publisher = AmwayDaily(
        docx_dir=str(docx_dir),
        work_dir=str(work_dir),
        queue_file=str(queue_file),
        theme="newspaper"  # 排版主题
    )
    
    success = publisher.run()
    
    if success:
        print("\n✅ 今日任务完成")
    else:
        print("\n❌ 今日任务失败或无内容")
        sys.exit(1)

if __name__ == "__main__":
    main()