#!/usr/bin/env python
"""
HTML 转 PDF 工具 (基于 Patchright/Playwright)
用法:
    python html_to_pdf.py article.html
    python html_to_pdf.py article.html -o output.pdf
    python html_to_pdf.py article.html -o output.pdf --format A4 --margin 1.5cm
"""
import argparse
import asyncio
import sys
from pathlib import Path

try:
    from patchright.async_api import async_playwright
except ImportError:
    print("❌ 错误: 未安装 patchright。请运行: pip install patchright")
    sys.exit(1)


async def generate_pdf(html_path: str, pdf_path: str, format_size: str, margin: str) -> bool:
    html_file = Path(html_path).resolve()
    if not html_file.exists():
        print(f"❌ 错误: HTML 文件不存在 -> {html_file}")
        return False

    # 如果未指定输出路径，则默认与 HTML 同名同目录，后缀改为 .pdf
    if not pdf_path:
        pdf_file = html_file.with_suffix(".pdf")
    else:
        pdf_file = Path(pdf_path).resolve()

    print(f"🔄 正在加载: {html_file.name}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 使用 file:/// 协议加载本地文件 (注意 Windows 下 as_posix 会转为正斜杠)
        await page.goto(f"file:///{html_file.as_posix()}")
        
        # 等待 1 秒确保字体和样式完全渲染
        await page.wait_for_timeout(1000)
        
        print(f"🖨️  正在生成 PDF: {pdf_file.name} ...")
        await page.pdf(
            path=str(pdf_file),
            format=format_size,
            print_background=True,  # 关键：保留背景色、渐变和阴影
            margin={
                "top": margin,
                "right": margin,
                "bottom": margin,
                "left": margin
            }
        )
        
        await browser.close()
        
    print(f"✅ PDF 生成成功: {pdf_file}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="HTML 转 PDF 工具 (基于 Patchright)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python html_to_pdf.py article.html
  python html_to_pdf.py article.html -o article.pdf
  python html_to_pdf.py article.html -o output.pdf --format A4 --margin 2cm
        """
    )
    parser.add_argument("html", help="输入的 HTML 文件路径")
    parser.add_argument("-o", "--output", default=None, help="输出的 PDF 文件路径 (默认与 HTML 同名)")
    parser.add_argument("--format", default="A4", help="页面尺寸 (默认 A4, 可选 Letter, A3 等)")
    parser.add_argument("--margin", default="1.5cm", help="页边距 (默认 1.5cm, 如 1cm, 20mm)")
    
    args = parser.parse_args()
    
    success = asyncio.run(generate_pdf(args.html, args.output, args.format, args.margin))
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()