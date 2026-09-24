#!/usr/bin/env python
"""
🖋️ 题词书写 CLI
用法:
python skills/inscription_writer/cli.py output/tang/feitian.png "飞天笑持莲，飘带曳云霞。"
python skills/inscription_writer/cli.py input.png "题词内容" -o output.png --position bottom_right
"""
import sys
import argparse
from pathlib import Path

project_root = Path(__file__).parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from skills.inscription_writer import InscriptionWriter

def main():
    parser = argparse.ArgumentParser(description="🖋️ 题词书写 Skill")
    parser.add_argument("image", help="输入图片路径")
    parser.add_argument("text", help="题词文本")
    parser.add_argument("-o", "--output", default=None, help="输出图片路径 (默认: 原图_inscribed.png)")
    parser.add_argument("--font-size", type=int, default=36, help="字号 (默认: 36)")
    parser.add_argument("--position", default="top_right", 
                        choices=["top_right", "top_left", "bottom_right", "bottom_left"],
                        help="位置 (默认: top_right)")
    parser.add_argument("--margin", type=int, default=50, help="边距 (默认: 50)")
    parser.add_argument("--max-chars", type=int, default=8, help="每列最大字数 (默认: 8)")
    
    args = parser.parse_args()

    writer = InscriptionWriter()
    
    # 自动生成输出路径
    if not args.output:
        p = Path(args.image)
        args.output = str(p.parent / f"{p.stem}_inscribed{p.suffix}")

    print(f"🖋️  开始题词: {args.text}")
    result = writer.write(
        image_path=args.image,
        text=args.text,
        output_path=args.output,
        font_size=args.font_size,
        position=args.position,
        margin=args.margin,
        max_chars_per_col=args.max_chars,
    )

    if result["status"] == "success":
        print(f"✅ 题词完成: {result['result']['output_path']}")
    else:
        print(f"❌ 失败: {result.get('error')}")
        sys.exit(1)

if __name__ == "__main__":
    main()