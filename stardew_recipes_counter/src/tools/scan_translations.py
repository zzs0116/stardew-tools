import json
import re
import os

# 1. 路径配置
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OBJECTS_PATH = os.path.join(BASE_DIR, "Data_Objects.json")

def scan_missing_translations():
    if not os.path.exists(OBJECTS_PATH):
        print(f"错误: 找不到文件 {OBJECTS_PATH}")
        print(f"请确认 Data_Objects.json 直接位于 {BASE_DIR} 目录下")
        return

    try:
        with open(OBJECTS_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"解析 JSON 出错: {e}")
        return
    
    found_paths = set()
    print(f"正在扫描 {len(data)} 个物品的本地化令牌...")

    for item_id, info in data.items():
        display_name = info.get("DisplayName", "")
        # 匹配格式: [LocalizedText Strings\资产路径:键值]
        match = re.search(r'\[LocalizedText (.*?):.*?\]', display_name)
        if match:
            path = match.group(1).replace("\\", "/") # 统一斜杠格式
            found_paths.add(path)
    
    if not found_paths:
        print("扫描完成：没有发现未解析的本地化令牌（可能已全部翻译）。")
    else:
        print(f"\n--- 扫描完成，共发现 {len(found_paths)} 个翻译源 ---")
        print("请在游戏存档加载后的 SMAPI 控制台执行以下指令：\n")
        for p in sorted(found_paths):
            print(f'patch export "{p}"')
        print(f"\n导出完成后，请将生成的 JSON 文件直接放到此目录下：\n{BASE_DIR}")

if __name__ == "__main__":
    scan_missing_translations()
