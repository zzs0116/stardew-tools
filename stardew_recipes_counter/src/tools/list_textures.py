import json
import os
import re

# 路径配置
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OBJECTS_PATH = os.path.join(BASE_DIR, "Data_Objects.json")
COMMANDS_FILE = os.path.join(BASE_DIR, "export_commands.txt")

def list_all_required_textures():
    if not os.path.exists(OBJECTS_PATH):
        print(f"错误：找不到 {OBJECTS_PATH}")
        return

    with open(OBJECTS_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    unique_textures = set()
    for item_id, info in data.items():
        # 1.6 版本逻辑：如果 Texture 缺失或是 null，则默认为原版贴图
        # 这里使用 or 确保即使字段是 null 也会变成默认值
        tex_path = info.get("Texture") or "Maps/springobjects"
        unique_textures.add(str(tex_path))

    # 排序（现在全是字符串了，不会报错）
    sorted_textures = sorted(list(unique_textures))

    print(f"--- 扫描完成 ---")
    print(f"共发现 {len(sorted_textures)} 个贴图资源。")
    
    # 将指令写入文件，省去手动复制粘贴
    with open(COMMANDS_FILE, "w", encoding="utf-8") as f:
        for tex in sorted_textures:
            if tex == "Maps/springobjects":
                continue
            f.write(f'patch export "{tex}" image\n')

    print(f"\n✅ 指令已生成至: {COMMANDS_FILE}")
    print("--------------------------------------------------")
    print("操作建议：")
    print("1. 打开该文本文件，分批次（例如每次 20 条）复制指令。")
    print("2. 在 SMAPI 控制台直接粘贴并回车。")
    print("3. 所有图标导出后，请将其移动到你的项目图片目录下。")

if __name__ == "__main__":
    list_all_required_textures()
