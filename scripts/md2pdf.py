#!/usr/bin/env python
"""
Markdown 转 PDF 简易工具 (基于 xhtml2pdf)
用法:
    python md2pdf.py article.md
    python md2pdf.py article.md -o output.pdf
    python md2pdf.py --help
"""
import argparse
import markdown
from xhtml2pdf import pisa
from pathlib import Path
import sys

# 注入中文字体支持（xhtml2pdf 默认不支持中文）
FONT_CSS = """
@font-face {
    font-family: "SimSun";
    src: url("C:/Windows/Fonts/simsun.ttc");
}
body { font-family: "SimSun", sans-serif; }
"""

def convert_md_to_pdf(md_path: str, pdf_path: str):
    """核心转换函数"""
    md_file = Path(md_path).resolve()
    pdf_file = Path(pdf_path).resolve()

    # 1. 校验输入文件
    if not md_file.exists():
        print(f"❌ 错误: Markdown 文件不存在 -> {md_file}")
        return False

    # 确保输出目录存在
    pdf_file.parent.mkdir(parents=True, exist_ok=True)

    print(f" 读取: {md_file}")
    with open(md_file, "r", encoding="utf-8") as f:
        md_content = f.read()

    # 2. Markdown 转 HTML
    html_text = markdown.markdown(
        md_content, 
        extensions=['tables', 'fenced_code']
    )
    
    # 3. 拼接字体样式 + 生成 PDF
    full_html = f"<style>{FONT_CSS}</style>\n{html_text}"
    
    print(f"💾 生成: {pdf_file}")
    with open(pdf_file, "w+b") as f:
        result = pisa.CreatePDF(full_html, dest=f, encoding="utf-8")
        
    # 4. 检查结果
    if result.err == 0:
        print(f"✅ 简易 PDF 已生成: {pdf_file}")
        return True
    else:
        print(f"❌ PDF 生成失败，错误码: {result.err}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Markdown 转 PDF 简易工具")
    parser.add_argument("input", help="输入的 Markdown 文件路径")
    parser.add_argument("-o", "--output", default=None, help="输出的 PDF 文件路径 (默认: 同名 .pdf)")
    
    args = parser.parse_args()
    
    # 如果未指定输出路径，自动生成
    output_path = args.output or str(Path(args.input).with_suffix(".pdf"))
    
    success = convert_md_to_pdf(args.input, output_path)
    sys.exit(0 if success else 1)