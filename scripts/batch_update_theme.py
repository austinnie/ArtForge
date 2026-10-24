import os
import re

# =========================================================
# ⚙️ 配置区：请确保这个路径是您存放 stone_carving 的目录
# =========================================================
TARGET_DIR = r"E:\SD_OpenVINO\ArtForge\presets\stone_carving"

def process_file(file_path):
    """处理单个 py 文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. 提取 name 的值 (兼容键名带空格的情况，如 "name ": "xxx ")
    name_match = re.search(r'"name"\s*:\s*"([^"]+)"', content)
    if not name_match:
        print(f"⚠️ 跳过 {os.path.basename(file_path)}: 未找到 'name' 字段")
        return
    
    # 提取 name 值并去除可能存在的首尾空格
    name_value = name_match.group(1).strip() 

    # 2. 查找并替换 "tags": [], (兼容键名带空格和缩进)
    # 正则解释：匹配行首缩进 + "tags" + 冒号 + [] + 可选逗号 + 行尾
    tags_pattern = re.compile(r'^(\s*)"tags"\s*:\s*\[\s*\],?\s*$', re.MULTILINE)
    
    def replacer(match):
        indent = match.group(1) # 保留原有的缩进（通常是4个空格）
        # 生成替换后的字符串，键名无空格，值无空格
        return f'{indent}"theme": "{name_value}",'

    new_content, count = tags_pattern.subn(replacer, content)

    # 3. 写回文件
    if count > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ 成功更新: {os.path.basename(file_path)}  ->  theme: \"{name_value}\"")
    else:
        print(f"⚠️ 跳过 {os.path.basename(file_path)}: 未找到 'tags': [] 字段")

if __name__ == "__main__":
    if not os.path.exists(TARGET_DIR):
        print(f"❌ 目录不存在，请检查路径: {TARGET_DIR}")
        input("按回车键退出...")
    else:
        print(f"🚀 开始批量处理目录: {TARGET_DIR}\n")
        file_count = 0
        for filename in os.listdir(TARGET_DIR):
            if filename.endswith(".py"):
                process_file(os.path.join(TARGET_DIR, filename))
                file_count += 1
        
        print(f"\n🎉 处理完成！共扫描 {file_count} 个 Python 文件。")
        input("按回车键退出...")