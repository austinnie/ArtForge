#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
gather_code.py
把项目源码合并为一个 txt，方便喂给 AI / 做代码备份。

用法:
    python gather_code.py                 # 默认输出 project_code_dump.txt
    python gather_code.py -o code.txt     # 自定义输出名
    python gather_code.py --max-size 256  # 单文件大小上限（KB），默认 512

改造要点:
1. 顶层排除: root 下的 output/、data/、logs/、tmp/、img_cache/、audio/、music*/、video*/
   等生成物目录整棵剪掉，遍历阶段就不进去，速度也快
2. 任意层级排除: __pycache__/.git/build/dist/data/logs/tmp 等
3. 后缀黑名单: 图片/音频/视频/文档/压缩包/字体/数据库/日志/模型权重
4. 二进制嗅探: 前 8KB 含 \\x00 的直接判为二进制
5. 大小上限: 超过 --max-size 的单文件跳过（防止大 json / 大 md 灌爆）
6. 自动排除输出文件自身，反复运行不会滚雪球
7. 结束后打印"跳过统计"，便于自查
"""
import argparse
import os
from pathlib import Path

# ==================== 配置区 ====================

# ---- 要收集的文件后缀（小写）----
INCLUDE_EXTS = {
    '.py', '.txt', '.json', '.env', '.md', '.yml', '.yaml',
    '.cfg', '.conf', '.xml', '.html', '.css', '.js',
    '.toml', '.ini', '.sh', '.bat', '.ps1', '.cmd',
    '.gitignore', '.dockerignore', '.editorconfig',
}

# ---- 即使白名单里有，也强制跳过的后缀 ----
EXCLUDE_EXTS = {
    # 图片
    '.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff', '.svg', '.ico',
    # 音频
    '.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg', '.mid', '.midi', '.sf2',
    # 视频
    '.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv',
    # 办公文档
    '.docx', '.doc', '.xlsx', '.xls', '.pptx', '.pdf', '.epub',
    # 压缩/二进制
    '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2',
    '.exe', '.dll', '.so', '.dylib', '.pyd',
    # Python 缓存
    '.pyc', '.pyo', '.pkl', '.pickle',
    # 数据库
    '.sqlite', '.sqlite3', '.db',
    # 字体
    '.ttf', '.otf', '.woff', '.woff2',
    # 日志
    '.log',
    # 打包产物
    '.pkg', '.toc', '.pyz', '.spec',
    # 模型权重
    '.safetensors', '.ckpt', '.bin', '.onnx',
}

# ---- 只在"项目根目录的第一层"排除（区分 output 缓存 vs skills 里的同名代码）----
EXCLUDE_TOP_DIRS = {
    # ★ 你原来就排除了这些代码目录，我原样保留；想收集 scripts/services/config/gui 等，
    #   把对应名字删掉即可（root 下同名目录才会被排除，skills 里的同名目录不受影响）
    'presets', 'scripts', 'settings', 'assets', 'gui',
    'services', 'config', 'layers',

    # 构建 / 发布
    'build', 'dist', 'release',

    # 运行产物（root/output 下包含 wechat/articles/daily/art_nude/机甲/油画/... 全部生成物）
    'output', 'outputs',

    # 媒体 / 播放器缓存
    'audio', 'music', 'music_player', 'video_player', 'radio_player',
    'multimedia', 'videos', 'images', 'search_engine',
    'qq_export_data', 'python_generated',
}

# ---- 任意层级都排除（名字足够独特，不会误伤代码目录）----
EXCLUDE_DIR_NAMES = {
    '__pycache__', '.git', '.svn', '.hg', '.venv', 'venv',
    'node_modules', '.idea', '.vscode',
    '.pytest_cache', '.mypy_cache', '.ruff_cache',
    '__pypackages__', 'site-packages',
    # 数据 / 日志 / 缓存
    'data', 'logs', 'tmp', 'temp',
    'img_cache', 'imgs_cache',
}

# ---- 明确不收集的文件名（不含敏感 .env 和自动生成的汇总文件）----
EXCLUDE_FILES = {
    '.env',                # 含 API Key
    '.cache.json',
    'lora_config',
    '.model_config',
    '.gitkeep',
    'list.txt',            # 目录清单，体积大且非代码
    'styles_list.txt',
}

# ---- 其它 ----
OUTPUT_FILE = 'project_code_dump.txt'
DEFAULT_MAX_KB = 512          # 单文件上限
BINARY_SNIFF_BYTES = 8192     # 二进制嗅探前多少字节

# ==================== 核心逻辑 ====================

def is_binary(path: Path) -> bool:
    """粗判二进制：前 N 字节含 \\x00 即视为二进制"""
    try:
        with open(path, 'rb') as f:
            return b'\x00' in f.read(BINARY_SNIFF_BYTES)
    except OSError:
        return True


def gather_files(root_dir: Path, output_name: str, max_bytes: int):
    files = []
    stats = {'ext': 0, 'name': 0, 'size': 0, 'binary': 0}

    for current_dir, dirs, filenames in os.walk(root_dir):
        cur = Path(current_dir)
        is_top = cur == root_dir

        # ① 目录剪枝（避免进入 out/ 等海量图片目录）
        kept = []
        for d in dirs:
            if d in EXCLUDE_DIR_NAMES:
                continue
            if is_top and d in EXCLUDE_TOP_DIRS:
                continue
            kept.append(d)
        dirs[:] = kept

        # ② 文件过滤
        for name in filenames:
            p = cur / name

            # 黑名单文件名 / 输出文件自身
            if name in EXCLUDE_FILES or name == output_name:
                stats['name'] += 1
                continue

            suffix = p.suffix.lower()

            # 后缀黑名单优先
            if suffix in EXCLUDE_EXTS:
                stats['ext'] += 1
                continue

            # 白名单：常规后缀 或 无后缀的点文件（.gitignore / .env.example 之类）
            if not (suffix in INCLUDE_EXTS or (not suffix and name.startswith('.'))):
                continue

            # 大小上限
            try:
                if p.stat().st_size > max_bytes:
                    stats['size'] += 1
                    continue
            except OSError:
                continue

            # 二进制嗅探
            if is_binary(p):
                stats['binary'] += 1
                continue

            files.append(p)

    return sorted(files), stats


def main():
    ap = argparse.ArgumentParser(description='汇总项目代码到单个 txt 文件')
    ap.add_argument('-o', '--output', default=OUTPUT_FILE, help='输出文件名')
    ap.add_argument('--max-size', type=int, default=DEFAULT_MAX_KB,
                    metavar='KB', help=f'单文件大小上限（KB），默认 {DEFAULT_MAX_KB}')
    args = ap.parse_args()

    root = Path.cwd()
    output_path = root / Path(args.output).name
    max_bytes = args.max_size * 1024

    print(f'📂 扫描目录: {root}')
    print(f'   排除的顶层目录: {", ".join(sorted(EXCLUDE_TOP_DIRS))}')

    files, stats = gather_files(root, output_path.name, max_bytes)
    if not files:
        print('⚠️  未找到符合条件的文件，请检查配置。')
        return

    print(f'📄 命中 {len(files)} 个文件，正在写入 {output_path.name} ...')

    with open(output_path, 'w', encoding='utf-8', errors='replace') as f:
        f.write(f'项目代码汇总 (扫描于 {root})\n')
        f.write(f'包含文件数: {len(files)}\n')
        f.write('=' * 80 + '\n\n')

        for p in files:
            rel = p.relative_to(root)
            f.write(f'=== 文件: {rel.as_posix()} ===\n')
            try:
                content = p.read_text(encoding='utf-8', errors='replace')
            except Exception as e:
                content = f'[读取失败: {e}]'
            f.write(content)
            if not content.endswith('\n'):
                f.write('\n')
            f.write('\n' + '-' * 40 + '\n\n')

    size_kb = output_path.stat().st_size // 1024
    print(f'✅ 完成: {output_path.name}  ({size_kb} KB, {len(files)} 个文件)')
    print(f'   跳过: 后缀黑名单 {stats["ext"]} · 文件名黑名单 {stats["name"]} · '
          f'超过 {args.max_size}KB {stats["size"]} · 二进制 {stats["binary"]}')


if __name__ == '__main__':
    main()