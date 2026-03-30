import json
import os
import re

DATA_DIR = "stardew_fish_by_season/data"

def is_chinese(string):
    """Check if a string contains mostly Chinese characters."""
    # This is a simple heuristic. If it contains english letters, we flag it.
    if not string or string == "未知": return True
    if re.search(r'[a-zA-Z]', string):
        return False
    return True

def main():
    untranslated = {}
    
    if not os.path.exists(DATA_DIR):
        print(f"Directory {DATA_DIR} not found.")
        return

    for filename in os.listdir(DATA_DIR):
        if not filename.endswith("_fish_data.json"): continue
        
        path = os.path.join(DATA_DIR, filename)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            for entry in data:
                loc = entry.get("位置")
                if loc and not is_chinese(loc):
                    if filename not in untranslated:
                        untranslated[filename] = set()
                    
                    # Locations are often comma/pause separated
                    parts = re.split(r'[、,]', loc)
                    for p in parts:
                        p = p.strip()
                        if not is_chinese(p):
                            untranslated[filename].add(p)
                            
        except Exception as e:
            print(f"Error reading {filename}: {e}")

    if not untranslated:
        print("All locations appear to be translated!")
    else:
        print("Found untranslated locations:")
        for filename, locs in untranslated.items():
            print(f"\n[{filename}]")
            for l in sorted(locs):
                print(f"  - {l}")

if __name__ == "__main__":
    main()
