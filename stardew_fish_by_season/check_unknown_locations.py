import json
import os
import glob

DATA_DIR = "stardew_fish_by_season/data"

def main():
    json_files = glob.glob(os.path.join(DATA_DIR, "*.json"))
    
    unknown_map = {} # source -> [fish_names]
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            for fish in data:
                loc = fish.get("位置")
                if not loc or loc == "未知":
                    source = fish.get("来源", "Unknown Source")
                    name = fish.get("名称", "Unknown Name")
                    
                    if source not in unknown_map:
                        unknown_map[source] = []
                    unknown_map[source].append(name)
                    
        except Exception as e:
            print(f"Error reading {json_file}: {e}")

    print(f"--- 位置未知的鱼类统计 ---")
    total_unknown = 0
    for source, names in unknown_map.items():
        print(f"\n【{source}】 ({len(names)} 条):")
        print("、".join(names))
        total_unknown += len(names)
    
    print(f"\n总计: {total_unknown} 条位置未知")

if __name__ == "__main__":
    main()
