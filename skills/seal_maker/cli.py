#!/usr/bin/env python
"""
 印章制作 CLI (支持单张 & 目录批量处理)
用法:
# 1. 生成独立印章 PNG
python seal_maker_cli.py make "東方藝術" --style zhu_wen --shape square --size 512 -o output.png

# 2. 单张图片盖章
python seal_maker_cli.py apply input.png "東方藝術" --position bottom_right --scale 0.15 -o output.png

# 3. 批量处理整个目录 (自动扫描 png/jpg，输出到 input_sealed 目录)
python seal_maker_cli.py apply output/tang "東方藝術" --position bottom_right --scale 0.14

# 4. 批量处理并指定输出目录
python seal_maker_cli.py apply output/tang "東方藝術" -o output/tang_final/
"""
import sys
import argparse
from pathlib import Path

project_root = Path(__file__).parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from skills.seal_maker import SealMaker

# 支持的图片格式
IMAGE_EXTS = {'.png', '.jpg', '.jpeg', '.webp', '.bmp'}

def cmd_make(args):
    """生成独立印章"""
    maker = SealMaker()
    result = maker.make_seal(
        text=args.text,
        style=args.style,
        shape=args.shape,
        size=args.size,
        output_path=args.output
    )
    if result["status"] == "success":
        print(f"✅ 印章已生成: {result.get('output_path', '内存中')}")
        print(f"   文字: {result['text']} | 样式: {result['style']} | 尺寸: {result['size']}")
    else:
        print(f"❌ 失败: {result.get('error')}")

def cmd_apply(args):
    """盖章（支持单张 & 目录批量）"""
    maker = SealMaker()
    input_path = Path(args.image)

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
            out_dir = input_path.parent / f"{input_path.name}_sealed"
        out_dir.mkdir(parents=True, exist_ok=True)

        print(f"🔄 开始批量处理目录: {input_path} (共 {len(images)} 张图片)")
        print(f"📂 输出目录: {out_dir}\n")
        
        success_count = 0
        for idx, img_file in enumerate(images, 1):
            # 构造单张的输出路径（原文件名 + _sealed）
            out_file = out_dir / f"{img_file.stem}_sealed{img_file.suffix}"
            print(f"  [{idx}/{len(images)}] {img_file.name} -> {out_file.name}")

            result = maker.apply_seal(
                image_path=str(img_file),
                text=args.text,
                position=args.position,
                style=args.style,
                shape=args.shape,
                scale=args.scale,
                margin=args.margin,
                output_path=str(out_file)
            )
            if result["status"] == "success":
                success_count += 1
            else:
                print(f"    ⚠️ 失败: {result.get('error')}")

        print(f"\n" + "="*50)
        print(f"✅ 批量处理完成！成功: {success_count}/{len(images)}")
        print(f"📂 输出目录: {out_dir}")
        print("="*50)

    # ================= 单张处理模式 =================
    else:
        if not input_path.exists():
            print(f"❌ 文件不存在: {input_path}")
            return
            
        # 单张未指定输出路径时，自动加后缀
        if not args.output:
            args.output = str(input_path.parent / f"{input_path.stem}_sealed{input_path.suffix}")

        result = maker.apply_seal(
            image_path=str(input_path),
            text=args.text,
            position=args.position,
            style=args.style,
            shape=args.shape,
            scale=args.scale,
            margin=args.margin,
            output_path=args.output
        )
        if result["status"] == "success":
            print(f"✅ 印章已贴到图片: {result.get('output_path')}")
            print(f"   文字: {result['text']} | 位置: {result['position']}")
        else:
            print(f"❌ 失败: {result.get('error')}")

def main():
    parser = argparse.ArgumentParser(description=" 印章制作工具 (支持批量)")
    sub = parser.add_subparsers(dest="command")
    
    # make 子命令
    p_make = sub.add_parser("make", help="生成独立印章图片（透明 PNG）")
    p_make.add_argument("text", help="印章文字")
    p_make.add_argument("--style", default="zhu_wen", choices=["zhu_wen", "bai_wen"], help="样式：朱文/白文")
    p_make.add_argument("--shape", default="square", choices=["square", "rect"], help="形状：方形/长方形")
    p_make.add_argument("--size", type=int, default=256, help="边长（px）")
    p_make.add_argument("-o", "--output", help="输出路径")
    
    # apply 子命令
    p_apply = sub.add_parser("apply", help="把印章贴到图片上 (支持传入目录批量处理)")
    p_apply.add_argument("image", help="输入图片路径 或 图片目录")
    p_apply.add_argument("text", help="印章文字")
    p_apply.add_argument("--position", default="bottom_right", 
                         choices=["top_left", "top_right", "bottom_left", "bottom_right"],
                         help="位置")
    p_apply.add_argument("--style", default="zhu_wen", choices=["zhu_wen", "bai_wen"])
    p_apply.add_argument("--shape", default="square", choices=["square", "rect"])
    p_apply.add_argument("--scale", type=float, default=0.12, help="相对图片短边的比例")
    p_apply.add_argument("--margin", type=int, default=40, help="边距（px）")
    p_apply.add_argument("-o", "--output", help="输出路径 (目录模式下为输出文件夹)")
    
    args = parser.parse_args()
    
    if args.command == "make":
        cmd_make(args)
    elif args.command == "apply":
        cmd_apply(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()