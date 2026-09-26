# scripts/test_ttf.py
"""
TTF 字体完整性检测工具

用法:
    python scripts/test_ttf.py                              # 默认测试项目自带小篆
    python scripts/test_ttf.py path/to/font.ttf             # 测试指定字体
    python scripts/test_ttf.py --full                       # 扫描全部 CJK 汉字（慢）
    python scripts/test_ttf.py --text "東方藝術"             # 只测指定字符
    python scripts/test_ttf.py --render                     # 生成可视化对比图
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PIL import Image, ImageDraw, ImageFont


DEFAULT_FONT = PROJECT_ROOT / "assets" / "fonts" / "Mini_zhuan.ttf"

# 默认测试字符集：印章/水印/题词常用字
DEFAULT_TEST_CHARS = (
    "東方藝術方艺术"
    "東东龍龙馬马天狗鞍山源氏物語"
    "百鬼夜行日月星辰山水花鳥風雪"
    "雲云春夏秋冬詩書畫印篆隸楷行草"
    "韻雅靜心清遠天地人和福壽康寧"
)

# CJK 统一汉字区
CJK_START = 0x4E00
CJK_END = 0x9FFF


def has_glyph(font: ImageFont.FreeTypeFont, char: str) -> bool:
    """检查字体是否包含某个字形的可见 mask"""
    if char.isspace():
        return True
    try:
        mask = font.getmask(char)
        return mask.size[0] > 1 and mask.size[1] > 1
    except Exception:
        return False


def check_chars(font_path: Path, chars: str, size: int = 80) -> tuple:
    """检查一组字符，返回 (supported, missing)"""
    try:
        font = ImageFont.truetype(str(font_path), size)
    except Exception as e:
        print(f"❌ 字体加载失败: {e}")
        sys.exit(1)

    supported = []
    missing = []
    for c in chars:
        if has_glyph(font, c):
            supported.append(c)
        else:
            missing.append(c)
    return supported, missing


def print_char_report(font_path: Path, chars: str, size: int = 80):
    """逐字打印支持情况"""
    try:
        font = ImageFont.truetype(str(font_path), size)
    except Exception as e:
        print(f"❌ 字体加载失败: {e}")
        return

    print(f"\n{'=' * 70}")
    print(f"字体: {font_path}")
    print(f"文件大小: {font_path.stat().st_size / 1024 / 1024:.2f} MB")
    try:
        print(f"字体名: {font.getname()}")
    except Exception:
        print(f"字体名: (无法读取)")
    print(f"{'=' * 70}\n")

    print(f"{'字符':<6}{'mask 大小':<16}{'状态':<8}")
    print("-" * 40)

    supported = []
    missing = []
    for c in chars:
        try:
            mask = font.getmask(c)
            ok = mask.size[0] > 1 and mask.size[1] > 1
            mark = "✅" if ok else "❌"
            print(f"  {c:<4}{str(mask.size):<16}{mark:<8}")
            if ok:
                supported.append(c)
            else:
                missing.append(c)
        except Exception as e:
            print(f"  {c:<4}ERROR: {e}")
            missing.append(c)

    print("\n" + "=" * 70)
    print(f"✅ 支持 ({len(supported)}): {''.join(supported)}")
    print(f"❌ 缺字 ({len(missing)}): {''.join(missing)}")
    print(f"\n支持率: {len(supported)}/{len(chars)} = "
          f"{len(supported) / max(1, len(chars)) * 100:.1f}%")
    print("=" * 70)

    return supported, missing


def scan_full_cjk(font_path: Path) -> list:
    """扫描全部 CJK 汉字，返回支持的字符列表"""
    try:
        font = ImageFont.truetype(str(font_path), 40)
    except Exception as e:
        print(f"❌ 字体加载失败: {e}")
        return []

    print(f"\n🔍 正在扫描 CJK 汉字 (U+4E00 - U+9FFF)...")
    supported = []
    total = CJK_END - CJK_START + 1
    for i, cp in enumerate(range(CJK_START, CJK_END + 1)):
        if i % 2000 == 0:
            print(f"  进度: {i}/{total} ({i / total * 100:.0f}%)")
        c = chr(cp)
        if has_glyph(font, c):
            supported.append(c)

    print(f"\n✅ 共支持 {len(supported)} 个汉字")
    print(f"\n完整列表:")
    print("".join(supported))
    return supported


def render_test(font_path: Path, chars: str, out_dir: Path):
    """生成可视化对比图"""
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        font = ImageFont.truetype(str(font_path), 80)
    except Exception as e:
        print(f"❌ 字体加载失败: {e}")
        return

    # 每个字符单独渲染，方便对照
    img = Image.new("RGB", (len(chars) * 100 + 40, 200), "white")
    d = ImageDraw.Draw(img)

    for i, c in enumerate(chars):
        x = 20 + i * 100
        d.text((x, 20), c, font=font, fill="black")
        d.text((x, 130), c, font=font, fill=(200, 200, 200))

    out_path = out_dir / "font_render_test.png"
    img.save(out_path)
    print(f"\n✅ 渲染测试图: {out_path}")

    # 同时生成每个字的放大版
    for i, c in enumerate(chars[:10]):  # 只画前 10 个
        single = Image.new("RGB", (200, 200), "white")
        sd = ImageDraw.Draw(single)
        sd.text((30, 30), c, font=font, fill="black")
        single.save(out_dir / f"char_{i:02d}_{ord(c):04X}.png")
    print(f"   单字放大图: {out_dir}/char_*.png")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("font", nargs="?", default=str(DEFAULT_FONT),
                    help="TTF 文件路径")
    ap.add_argument("--text", "-t", default=DEFAULT_TEST_CHARS,
                    help="测试字符集")
    ap.add_argument("--full", action="store_true",
                    help="扫描全部 CJK 汉字（慢）")
    ap.add_argument("--render", "-r", action="store_true",
                    help="生成可视化对比图")
    args = ap.parse_args()

    font_path = Path(args.font)
    if not font_path.exists():
        print(f"❌ 字体不存在: {font_path}")
        sys.exit(1)

    # 逐字报告
    print_char_report(font_path, args.text)

    # 全量扫描
    if args.full:
        scan_full_cjk(font_path)

    # 渲染测试
    if args.render:
        out_dir = PROJECT_ROOT / "output" / "tmp" / "font_test"
        render_test(font_path, args.text, out_dir)


if __name__ == "__main__":
    main()