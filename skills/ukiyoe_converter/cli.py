#!/usr/bin/env python
"""
🎨 浮世绘转换器 CLI (支持单张 & 目录批量处理)
用法:
# 1. 单张图片转换
python ukiyoe_converter_cli.py photo.jpg
python ukiyoe_converter_cli.py photo.jpg --engine agnes --strength 0.85 -o output.png

# 2. 批量处理整个目录 (自动扫描 png/jpg，输出到 input_ukiyoe 目录)
python ukiyoe_converter_cli.py output/tang
python ukiyoe_converter_cli.py output/tang --engine agnes --strength 0.8

# 3. 批量处理并指定输出目录 + 自定义印章
python ukiyoe_converter_cli.py output/tang --seal "李白" --seal-pos top_left -o output/tang_ukiyoe/
"""
import sys
import argparse
from pathlib import Path

project_root = Path(__file__).parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from skills.ukiyoe_converter import UkiyoeConverter

# 支持的图片格式
IMAGE_EXTS = {'.png', '.jpg', '.jpeg', '.webp', '.bmp'}

def cmd_convert(args):
    converter = UkiyoeConverter()
    input_path = Path(args.input)

    # ================= 批量处理模式 =================
    if input_path.is_dir():
        # 扫描图片
        images = [p for p in input_path.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTS]
        if not images:
            print(f"❌ 目录 {input_path} 下没有找到图片文件")
            return
        
        # 确定输出目录
        if args.output:
            out_dir = Path(args.output)
        else:
            out_dir = input_path.parent / f"{input_path.name}_ukiyoe"
        out_dir.mkdir(parents=True, exist_ok=True)

        print(f"🔄 开始批量转换: {input_path} (共 {len(images)} 张图片)")
        print(f"📂 输出目录: {out_dir}\n")
        
        success_count = 0
        for idx, img_file in enumerate(images, 1):
            # 构造单张的输出路径
            out_file = out_dir / f"{img_file.stem}_ukiyoe{img_file.suffix}"
            print(f"  [{idx}/{len(images)}] {img_file.name} -> {out_file.name}")

            # 应用命令行参数覆盖配置
            config_override = {}
            if args.seal_style: config_override["seal_style"] = args.seal_style
            if args.seal_pos: config_override["seal_position"] = args.seal_pos
            if config_override:
                converter.config.update(config_override)

            result = converter.convert(
                image_path=str(img_file),
                output_path=str(out_file),
                engine_name=args.engine,
                strength=args.strength,
                seal_text=args.seal,
            )
            if result["status"] == "success":
                success_count += 1
            else:
                print(f"    ️ 失败: {result.get('error')}")

        print(f"\n" + "="*50)
        print(f"✅ 批量转换完成！成功: {success_count}/{len(images)}")
        print(f"📂 输出目录: {out_dir}")
        print("="*50)

    # ================= 单张处理模式 =================
    else:
        if not input_path.exists():
            print(f"❌ 文件不存在: {input_path}")
            return
            
        # 单张未指定输出路径时，自动加后缀
        if not args.output:
            args.output = str(input_path.parent / f"{input_path.stem}_ukiyoe{input_path.suffix}")

        print(f"\n 浮世绘转换: {args.input}")
        result = converter.convert(
            image_path=args.input,
            output_path=args.output,
            engine_name=args.engine,
            strength=args.strength,
            seal_text=args.seal,
        )

        if result["status"] == "success":
            data = result["result"]
            print(f"\n✅ 转换完成！")
            print(f"    输出: {data['output_path']}")
            print(f"   🎨 引擎: {data['engine']}")
            print(f"   💪 强度: {data['strength']}")
            print(f"   🔖 印章: {data['seal_text']}")
            print(f"   ⏱️  耗时: {data['elapsed']}")
        else:
            print(f"\n❌ 转换失败: {result.get('error')}")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="🎨 浮世绘风格转换器（支持单张 & 目录批量）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python ukiyoe_converter_cli.py photo.jpg
  python ukiyoe_converter_cli.py output/tang --engine agnes --strength 0.85
  python ukiyoe_converter_cli.py output/tang --seal "李白" --seal-pos top_left -o output/tang_ukiyoe/
        """,
    )
    parser.add_argument("input", help="输入图片路径 或 图片目录")
    parser.add_argument("-o", "--output", default=None, help="输出路径 (目录模式下为输出文件夹)")
    parser.add_argument("--engine", default=None, help="引擎名称 (pollinations / agnes)")
    parser.add_argument("--strength", type=float, default=None, help="转换强度 0-1 (默认 0.75)")
    parser.add_argument("--seal", default=None, help="印章文字 (默认 東方藝術)")
    parser.add_argument("--seal-style", default=None, choices=["zhu_wen", "bai_wen"], help="印章样式")
    parser.add_argument("--seal-pos", default=None, choices=["top_left", "top_right", "bottom_left", "bottom_right"], help="印章位置")

    args = parser.parse_args()
    cmd_convert(args)

if __name__ == "__main__":
    main()