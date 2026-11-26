import os

# 目标要扫描的目录
TARGET_DIR = r"E:\SD_OpenVINO\ArtForge\skills\social_auto_upload"
# 输出文件的名字
OUTPUT_FILE = r"E:\SD_OpenVINO\ArtForge\social_auto_upload_dump.txt"

# 需要包含的文件后缀
VALID_EXTENSIONS = {'.py', '.json', '.md', '.toml', '.cmd', '.txt'}
# 需要跳过的文件夹（缓存、日志、生成的媒体、虚拟环境等）
IGNORE_DIRS = {'__pycache__', 'logs', 'videos', '.git', 'social_auto_upload.egg-info', 'static'}

def dump_code():
    print(f"开始扫描: {TARGET_DIR}")
    file_count = 0
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as outfile:
        outfile.write(f"项目代码汇总 (扫描于 {TARGET_DIR})\n")
        outfile.write("=" * 80 + "\n\n")

        for root, dirs, files in os.walk(TARGET_DIR):
            # 过滤掉不需要的目录
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in VALID_EXTENSIONS:
                    file_path = os.path.join(root, file)
                    # 获取相对路径用于显示
                    rel_path = os.path.relpath(file_path, TARGET_DIR)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            content = infile.read()
                            
                        # 写入分隔符和文件信息
                        outfile.write(f"=== 文件: {rel_path} ===\n")
                        outfile.write(content)
                        outfile.write("\n\n" + "-" * 80 + "\n\n")
                        file_count += 1
                        print(f"已提取: {rel_path}")
                    except Exception as e:
                        print(f"读取失败 {rel_path}: {e}")

    print(f"\n✅ 提取完成！共提取 {file_count} 个文件。")
    print(f"📄 汇总文件保存在: {OUTPUT_FILE}")
    print("请将这个 txt 文件发送给我分析。")

if __name__ == "__main__":
    dump_code()