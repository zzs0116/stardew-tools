import json
import os
import shutil
import re
import sys
from collections import defaultdict

# Add venv site-packages to path to use PIL
sys.path.append("../stardew_recipes_counter/src/venv/lib/python3.14/site-packages")
from PIL import Image

# Configuration
DATA_OBJECTS_PATH = "../stardew_recipes_counter/src/Data_Objects.json"
STRINGS_PATH = "../stardew_recipes_counter/src/Strings_Objects.json"
ASSETS_PATH = "../stardew_recipes_counter/src/assets"
DATA_DIR = "data"
IMAGES_DIR = "images"
DATA_FISH_PATH = "Data_Fish.json"
DATA_LOCATIONS_PATH = "Data_Locations.json"
LOCATIONS_ZH_DIR = "locations_zh_cn"

# File Mappings
PREFIX_MAP = {
    "Rafseazz.RSVCP": "ridgeside",
    "Ridgeside": "ridgeside",
    "FlashShifter.StardewValleyExpanded": "sve",
    "Lemurkat.EastScarp": "eastscarp",
    "Mods_MNF": "mnf",
    "MNF": "mnf",
    "Mods_Lumisteria.MtVapius": "mtvapius",
    "Lumisteria.MtVapius": "mtvapius",
    "Mods_DTZ": "dtz",
    "DTZ": "dtz",
    "skellady.SBVCP": "sbvcp",
    "Textures_7thAxis.LitD": "litd",
    "StardewValley": "vanilla" # Default/Fallback
}

FILE_MAP = {
    "vanilla": "fish_data.json",
    "ridgeside": "ridgeside_fish_data.json",
    "sve": "sve_fish_data.json",
    "eastscarp": "eastscarp_fish_data.json",
    "mnf": "mnf_fish_data.json",
    "mtvapius": "mtvapius_fish_data.json",
    "dtz": "dtz_fish_data.json",
    "sbvcp": "sbvcp_fish_data.json",
    "litd": "litd_fish_data.json"
}

SOURCE_NAME_MAP = {
    "vanilla": "原版",
    "ridgeside": "里奇赛德",
    "sve": "SVE",
    "eastscarp": "东斯卡普",
    "mnf": "更多的鱼",
    "mtvapius": "迷雾山",
    "dtz": "祖祖城",
    "sbvcp": "阳莓村",
    "litd": "Life in the Deep"
}

def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def resolve_string(text, strings_map):
    if not text:
        return ""
    if isinstance(text, str) and text.startswith("[LocalizedText"):
        match = re.search(r'Strings\\Objects:([^]]+)', text)
        if match:
            key = match.group(1)
            return strings_map.get(key, text)
        match = re.search(r':([^]]+)', text)
        if match:
            key = match.group(1)
            return strings_map.get(key, text)
    return text

def determine_source(item_id, texture_path):
    # Special overrides for specific items to move to Vanilla
    if item_id in ["Goby", "CaveJelly", "RiverJelly", "SeaJelly"]:
        return "vanilla"

    for prefix, source in PREFIX_MAP.items():
        if prefix in item_id or (texture_path and prefix in texture_path):
            return source
    
    if str(item_id).isdigit():
        return "vanilla"
        
    # Default fallback changed from "other" to "eastscarp"
    return "eastscarp"

def crop_sprite(source_image_path, dest_image_path, sprite_index, item_size=16):
    """Crops a specific sprite from a spritesheet."""
    try:
        with Image.open(source_image_path) as img:
            width, height = img.size
            
            # If image is already 16x16 (or close to single item), no need to crop
            if width <= item_size and height <= item_size:
                shutil.copy2(source_image_path, dest_image_path)
                return True

            cols = width // item_size
            if cols == 0: cols = 1
            
            row = sprite_index // cols
            col = sprite_index % cols
            
            x = col * item_size
            y = row * item_size
            
            # Boundary check
            if x + item_size > width or y + item_size > height:
                print(f"Warning: Sprite index {sprite_index} out of bounds for {source_image_path} ({width}x{height})")
                return False
                
            cropped = img.crop((x, y, x + item_size, y + item_size))
            cropped.save(dest_image_path)
            return True
    except Exception as e:
        print(f"Error cropping {source_image_path}: {e}")
        return False

def find_and_process_image(item_id, item_name, texture_path, source, sprite_index):
    # Target directory
    target_dir = os.path.join(IMAGES_DIR, source)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir, exist_ok=True)
        
    sanitized_name = item_name.replace(" ", "_").replace("'", "")
    target_filename = f"{sanitized_name}.png"
    target_path = os.path.join(target_dir, target_filename)
    
    # If target already exists and is small (cropped), use it
    if os.path.exists(target_path):
        # Optional: check if we need to regenerate? For now assume existing is good if correct name
        return f"./images/{source}/{target_filename}"

    # Search for source image
    source_candidates = []
    
    # 1. Texture path derived
    if texture_path:
        clean_texture = texture_path.replace("\\", "_").replace("/", "_")
        source_candidates.append(f"{clean_texture}.png")
        texture_filename = os.path.basename(texture_path.replace("\\", "/"))
        source_candidates.append(f"{texture_filename}.png")
    
    # 2. Name derived
    source_candidates.append(f"{item_id}.png")
    source_candidates.append(f"{sanitized_name}.png")
    source_candidates.append(f"{source}_{sanitized_name}.png")

    found_source = None
    for filename in os.listdir(ASSETS_PATH):
        if filename in source_candidates:
            found_source = os.path.join(ASSETS_PATH, filename)
            break
    
    # Fallback for vanilla items: Use Maps_springobjects.png
    if not found_source and source == "vanilla":
        springobjects_path = os.path.join(ASSETS_PATH, "Maps_springobjects.png")
        if os.path.exists(springobjects_path):
            found_source = springobjects_path
            
    if found_source:
        # Check if needs cropping
        if sprite_index is not None and sprite_index >= 0:
            success = crop_sprite(found_source, target_path, sprite_index)
            if success:
                return f"./images/{source}/{target_filename}"
        
        # Fallback: just copy
        shutil.copy2(found_source, target_path)
        return f"./images/{source}/{target_filename}"

    return ""

def parse_time(time_str):
    # "600 2600" -> "06:00 - 02:00"
    if not time_str: return ""
    if time_str.strip() == "600 2600":
        return "任意时间"
    
    parts = time_str.split(' ')
    formatted_intervals = []
    
    def to_clock(v):
        try:
            v = int(v)
        except:
            return v
        h = v // 100
        m = v % 100
        while h >= 24: h -= 24
        return f"{h:02d}:{m:02d}"

    for i in range(0, len(parts), 2):
        if i+1 >= len(parts): break
        start = parts[i]
        end = parts[i+1]
        interval = f"{to_clock(start)} - {to_clock(end)}"
        if interval == "06:00 - 02:00":
            interval = "任意时间"
        formatted_intervals.append(interval)
        
    return ", ".join(formatted_intervals)

def parse_weather(w):
    mapping = {
        "sunny": "晴天",
        "rainy": "雨天",
        "storm": "雷雨",
        "both": "任意天气"
    }
    return mapping.get(w, w)

def parse_season(s):
    # "spring summer"
    parts = s.split(' ')
    mapping = {
        "spring": "春季",
        "summer": "夏季",
        "fall": "秋季",
        "winter": "冬季"
    }
    return "、".join([mapping.get(p, p) for p in parts])

def remove_comments(json_str):
    # Remove // comments
    json_str = re.sub(r'//.*', '', json_str)
    # Remove /* */ comments
    json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
    # Remove trailing commas
    json_str = re.sub(r',(\s*[\}\]])', r'\1', json_str)
    return json_str

def load_location_translations(directory):
    print("Loading location translations...")
    translations = {}
    
    if not os.path.exists(directory):
        print(f"Warning: Localization directory {directory} not found.")
        return translations

    for filename in os.listdir(directory):
        if not filename.endswith(".json"): continue
        
        path = os.path.join(directory, filename)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                cleaned_content = remove_comments(content)
                data = json.loads(cleaned_content)
            
            # Flatten or parse keys
            for key, val in data.items():
                if not isinstance(val, str): continue
                
                # RSV style: "Custom_Ridgeside_Ridge.Name": "山脊"
                if key.startswith("Custom_") and key.endswith(".Name"):
                    internal_name = key[:-5] # Remove .Name
                    translations[internal_name] = val
                    continue
                
                # SVE style: "DisplayName.GrandpasShed": "爷爷的小屋"
                if key.startswith("DisplayName."):
                    internal_name = key[12:] # Remove DisplayName.
                    # SVE often uses Custom_Prefix internally, need to match loosely or map
                    translations[internal_name] = val
                    translations["Custom_" + internal_name] = val
                    continue
                
                # SVE LocationData: "LocationData.Grandpas_Shed_Outside"
                if key.startswith("LocationData."):
                    internal_name = key[13:] # e.g. Grandpas_Shed_Outside
                    translations[internal_name] = val
                    translations[internal_name.replace("_", "")] = val # GrandpasShedOutside
                    translations[internal_name.replace("_", " ")] = val # Grandpas Shed Outside
                    continue
                
                # EastScarp: "EastScarp.Locations.DeepMountains" -> "EastScarp DeepMountains"
                if key.startswith("EastScarp.Locations."):
                    sub_name = key[20:] # DeepMountains
                    translations[sub_name] = val
                    translations[f"EastScarp_{sub_name}"] = val
                    continue
                
                # SBV (Sunberry): "Sunberry.Locations.SunberryVillage" -> "SunberryVillage"
                if key.startswith("Sunberry.Locations."):
                    sub_name = key[19:]
                    translations[sub_name] = val
                    continue

        except Exception as e:
            print(f"Error parsing {filename}: {e}")
            
    # Hardcoded supplements for complex cases or missing keys
    manual_map = {
        # Downtown Zuzu
        "Custom_DTZ_ZuzuCity1": "祖祖城",
        "Custom_DTZ_ZuzuCityFreeway1": "祖祖城高速公路",
        "Custom_DTZ_ZuzuCityOasis1": "祖祖城绿洲",
        "Custom_DTZ_ResortCentral": "祖祖城度假村",
        "Custom_DTZ_Sewer": "祖祖城下水道",
        "Custom_DTZ_Underground1": "祖祖城地下",
        
        # SVE
        "Custom_GrandpasShed": "爷爷的小屋",
        "Custom_GrandpasShedGreenhouse": "爷爷的温室",
        "Custom_BlueMoonVineyard": "蓝月亮葡萄园",
        "Custom_AuroraVineyard": "极光葡萄园",
        "Custom_SpriteSpring": "精灵之泉",
        "SpriteSpring2": "精灵之泉",
        "Custom_JunimoWoods": "祝尼魔森林",
        "Custom_ForestWest": "西部森林",
        "Custom_CrimsonBadlands": "绯红荒地",
        "CrimsonBadlands": "绯红荒地",
        "Highlands": "高地",
        "Custom_Highlands": "高地",
        "MorrisProperty": "莫里斯地产",
        "Custom_MorrisProperty": "莫里斯地产",
        "AdventurerSummit": "探险家山峰",
        "Custom_AdventurerSummit": "探险家山峰",
        "FerngillRepublicFrontier": "芬吉尔共和国边境",
        "Custom_FerngillRepublicFrontier": "芬吉尔共和国边境",
        
        # East Scarp
        "Custom_EastScarp_Village": "东斯卡普",
        "Custom_EastScarp_DeepDark": "悬崖之下",
        "Custom_EastScarp_Orchard": "樱桃园",
        "EastScarp_Village": "东斯卡普",
        "EastScarp Village": "东斯卡普",
        "EastScarp_DeepMountains": "深山",
        "EastScarp DeepMountains": "深山",
        "EastScarp_SeaCave": "东斯卡普海边洞窟",
        "EastScarp SeaCave": "东斯卡普海边洞窟",
        "EastScarp_SmugglerDen": "走私者的藏身地",
        "EastScarp SmugglerDen": "走私者的藏身地",
        "EastScarp_Orchard": "樱桃园",
        "EastScarp Orchard": "樱桃园",
        "EastScarp_HectorForest": "赫克托森林",
        "EastScarp HectorForest": "赫克托森林",
        "EastScarp_Underforge": "地下锻造厂",
        "EastScarp Underforge": "地下锻造厂",
        "EastScarp_FairyPool": "仙女池塘",
        "EastScarp FairyPool": "仙女池塘",
        
        # Mt Vapius (VMV)
        "Custom_Lumisteria_MtVapius_Summit": "雾呜山峰顶",
        "Custom_Lumisteria_MtVapius_Forest": "雾呜森林",
        "Custom_Lumisteria_MtVapius_Spring": "雾呜之泉",
        "Lumisteria.MtVapius_TrainStation": "雾呜山火车站",
        "Lumisteria.MtVapius_Main": "雾呜山",
        "Lumisteria.MtVapius_Forest": "雾呜森林",
        "Lumisteria.MtVapius_Hamlet": "雾呜山峰 - 珀光小区",
        "Lumisteria.MtVapius_Cliff": "雾呜山峰 - 悬崖",
        "Lumisteria.MtVapius_ForestTrailPond": "雾呜山峰 - 森林步道池塘",
        "Lumisteria.MtVapius_Faycombe": "仙子谷",
        "Lumisteria.MtVapius_FaycombeMeadow": "仙子谷草原",
        "Lumisteria.MtVapius_ForestCrystalLake": "森林水晶湖",
        "Lumisteria.MtVapius_ForestCaveLush": "森林洞穴-繁茂",
        "Lumisteria.MtVapius ForestCaveLush": "森林洞穴-繁茂",
        "Lumisteria.MtVapius_ForestCaveShortcut": "森林洞穴-捷径",
        "Lumisteria.MtVapius ForestCaveShortcut": "森林洞穴-捷径",
        "Lumisteria.MtVapius_ForestCaveStar": "森林洞穴-星",
        "Lumisteria.MtVapius ForestCaveStar": "森林洞穴-星",
        "Lumisteria.MtVapius_ForestCaveMoonPond": "森林洞穴-月亮池",
        "Lumisteria.MtVapius ForestCaveMoonPond": "森林洞穴-月亮池",
        "ForestCaveMoonPond": "森林洞穴-月亮池",
        "Lumisteria.MtVapius_ForestCaveMarsh": "森林洞穴-沼泽",
        "Lumisteria.MtVapius ForestCaveMarsh": "森林洞穴-沼泽",
        
        # Bear Fam
        "MadDog.BearFam.BearLodge Cliff": "熊小屋地下室",
        "MadDog.BearFam.Custom_BearLodge_Cliff": "熊小屋地下室",
        
        # East Scarp Additional
        "EastScarp_UnderwaterLexi": "海洋深处",
        "EastScarp_PirateShipReef": "海盗船礁",
        "EastScarp_Crossing": "东斯卡普路口",
        
        # Vanilla / Misc
        "Backwoods": "后山",
        "fishingGame": "钓鱼游戏",
        "Temp": "临时区域",
        "Custom_Ridgeside_RSVWestCliff": "西崖",
        "Custom_Ridgeside_RSVCliff_AlissaDate": "山脊崖边 (约会)",
        "Custom_Ridgeside_RSVCliff_FayeDate": "山脊崖边 (约会)",
        "BeachNightMarket": "夜市",
        
        # Others
        "Town": "鹈鹕镇",
        "Mountain": "山区", 
        "Beach": "海滩", 
        "Forest": "森林", 
        "Railroad": "铁路", 
        "Sewer": "下水道", 
        "BugLand": "突变虫穴", 
        "WitchSwamp": "女巫沼泽", 
        "UndergroundMine": "矿井", 
        "Desert": "沙漠", 
        "Woods": "秘密森林", 
        "IslandSouth": "姜岛南部", 
        "IslandWest": "姜岛西部", 
        "IslandNorth": "姜岛北部", 
        "IslandSouthEast": "姜岛东南部", 
        "IslandSouthEastCave": "海盗湾",
        "Submarine": "夜市潜水艇",
        "TenebrousNova.EliDylan.CP OldWoods": "古老森林",
        "TenebrousNova.EliDylan.CP_OldWoods": "古老森林",
        
        # Farms
        "Farm_Forest": "森林农场",
        "Farm_FourCorners": "四角农场",
        "Farm_Hilltop": "山顶农场",
        "Farm_Riverland": "河边农场",
        "Farm_Standard": "标准农场",
        "Farm_Wilderness": "荒野农场",
        
        # SVE
        "Custom_HenchmanBackyard": "亲信的后院",
        
        # Bear Fam
        "MadDog.BearFam.Custom_BearFamNoKrakenMap": "海怪洞窟",
        
        # Eli & Dylan
        "TenebrousNova.EliDylan.CP_EDMushroomCave": "蘑菇洞穴",
        
        # DTZ
        "Custom_DTZ_ResortSouth": "祖祖城度假村南部",
        "Custom_DTZ_ResortSouthWest": "祖祖城度假村西南部",
        
        # Vanilla
        "Caldera": "火山口"
    }
    
    translations.update(manual_map)
    return translations

def parse_locations_data(data, translations):
    # Map ItemId -> {
    #   "locations_by_season": { "spring": set(), "summer": set(), "fall": set(), "winter": set(), "all": set() },
    #   "seasons": set(),
    #   "weathers": set(), 
    #   "times": set()
    # }
    fish_map = defaultdict(lambda: {
        "locations_by_season": defaultdict(set),
        "seasons": set(),
        "weathers": set(), 
        "times": set()
    })
    
    for loc_key, loc_data in data.items():
        if loc_key == "Default": continue
        fish_list = loc_data.get("Fish")
        if not fish_list: continue
        
        # Translate location name
        loc_name = translations.get(loc_key)
        
        # Try stripping prefixes if not found
        if not loc_name:
            if loc_key.startswith("Custom_SBV_"):
                loc_name = translations.get(loc_key[11:]) # Strip Custom_SBV_
            elif loc_key.startswith("Lumisteria.MtVapius_"):
                loc_name = translations.get(loc_key[20:]) # Strip Lumisteria.MtVapius_
            elif loc_key.startswith("EastScarp_"):
                loc_name = translations.get(loc_key[10:]) # Strip EastScarp_
            elif loc_key.startswith("Custom_"):
                loc_name = translations.get(loc_key[7:]) # Strip Custom_
        
        # Last resort cleanup
        if not loc_name:
            loc_name = loc_key.replace("Custom_", "").replace("_", " ")
            # Try to match partial?
            pass
            
        for f in fish_list:
            item_id = f.get("ItemId") or f.get("Id")
            if not item_id: continue
            
            # Normalize ID: (O)123 -> 123, (O)Mod.Id -> Mod.Id
            # Note: Some mods don't use (O) prefix in Data/Locations
            clean_id = item_id.replace("(O)", "")
            
            # Determine seasons for this specific spawn entry
            entry_seasons = set()
            
            # 1. explicit 'Season' field
            if f.get("Season"):
                s_val = f.get("Season").lower()
                entry_seasons.add(s_val)
                fish_map[clean_id]["seasons"].add(s_val)
            
            # 2. Condition field
            cond = f.get("Condition")
            if cond:
                # LOCATION_SEASON Here Spring Summer
                season_match = re.search(r"LOCATION_SEASON Here ([a-zA-Z\s]+)", cond, re.IGNORECASE)
                if season_match:
                    founds = season_match.group(1).lower().split()
                    for s in founds:
                        if s in ["spring", "summer", "fall", "winter"]:
                            entry_seasons.add(s)
                            fish_map[clean_id]["seasons"].add(s)
            
            # If no season constraints found in Location data, add to "all" bucket
            if not entry_seasons:
                fish_map[clean_id]["locations_by_season"]["all"].add(loc_name)
            else:
                for s in entry_seasons:
                    fish_map[clean_id]["locations_by_season"][s].add(loc_name)
            
            # Weather
            if cond:
                cond_lower = cond.lower()
                if "weather here rain" in cond_lower:
                    fish_map[clean_id]["weathers"].add("rainy")
                elif "weather here sun" in cond_lower:
                    fish_map[clean_id]["weathers"].add("sunny")
                elif "weather here storm" in cond_lower:
                    fish_map[clean_id]["weathers"].add("storm")
                
                # Time
                time_match = re.search(r"TIME (\d+) (\d+)", cond)
                if time_match:
                    fish_map[clean_id]["times"].add(f"{time_match.group(1)} {time_match.group(2)}")

    return fish_map

def main():
    print("Loading data...")
    objects = load_json(DATA_OBJECTS_PATH)
    strings = load_json(STRINGS_PATH)
    
    # Load Game Fish Data
    fish_game_data = {}
    if os.path.exists(DATA_FISH_PATH):
        fish_details_raw = load_json(DATA_FISH_PATH)
        for fid, val in fish_details_raw.items():
            fields = val.split('/')
            
            # Handle Crab Pot Fish (Type 'trap')
            # Example: "715": "Lobster/trap/.05/688 .45 689 .35 690 .35/ocean/2/20/false"
            if len(fields) >= 5 and fields[1] == 'trap':
                loc_type = fields[4]
                # Map location types
                loc_name = "海洋 (蟹笼)" if loc_type == "ocean" else "淡水 (蟹笼)"
                
                fish_game_data[fid] = {
                    "is_trap": True,
                    "location": loc_name
                }
                continue

            if len(fields) < 8: continue
            
            fish_game_data[fid] = {
                "time": fields[5],
                "season": fields[6],
                "weather": fields[7]
            }
    else:
        print(f"Warning: {DATA_FISH_PATH} not found.")

    # Load Location Data
    fish_loc_info = {}
    if os.path.exists(DATA_LOCATIONS_PATH):
        print("Parsing Location Data...")
        # Load Translations
        loc_translations = load_location_translations(LOCATIONS_ZH_DIR)
        
        loc_data = load_json(DATA_LOCATIONS_PATH)
        fish_loc_info = parse_locations_data(loc_data, loc_translations)
    else:
        print(f"Warning: {DATA_LOCATIONS_PATH} not found.")

    # Load Manual Overrides
    overrides = load_json("manual_overrides.json")
    if overrides:
        print(f"Loaded {len(overrides)} manual overrides.")

    fish_data_map = {}
    for source, filename in FILE_MAP.items():
        # Initialize empty list to rebuild from scratch based on Data_Objects
        fish_data_map[source] = []

    print(f"Processing {len(objects)} objects...")
    
    count_processed = 0
    
    excluded_names = ["垃圾", "湿透的报纸", "浮木", "一张签名照", "破损的眼镜", "破损的 CD"]
    
    legendary_fish_names = [
        "传说之鱼", "绯红鱼", "𩽾𩾌鱼", "变种鲤鱼", "冰川鱼", 
        "炮塔鱼", "狼鲷", "深山𩽾𩾌鱼", "红鲑", "瀑布黑鱼", 
        "铱金鱼", "阴", "阳", "木须", "死魂虫", "异变鱼", 
        "小𩽾𩾌鱼", "巨鲟", "高山红点鲑王子", "行星鱼"
    ]

    for item_id, item in objects.items():
        if item.get("Type") != "Fish":
            continue
            
        if "foxbloom" in str(item_id).lower():
            continue

        name_raw = item.get("Name", "Unknown")
        display_name_raw = item.get("DisplayName", name_raw)
        
        display_name = resolve_string(display_name_raw, strings)
        
        # Check against blacklist
        if display_name in excluded_names:
            continue
            
        description_raw = item.get("Description", "")
        price = item.get("Price", 0)
        texture_path = item.get("Texture", "")
        sprite_index = item.get("SpriteIndex", 0)
        
        display_name = resolve_string(display_name_raw, strings)
        description = resolve_string(description_raw, strings)
        
        source = determine_source(item_id, texture_path)
        
        # Process Image (Find -> Crop -> Save)
        image_url = find_and_process_image(item_id, name_raw, texture_path, source, sprite_index)
        
        fisher_price = int(price * 1.25)
        angler_price = int(price * 1.5)
        
        qualities = [1, 1.25, 1.5, 2]
        price_lines = []
        fisher_lines = []
        angler_lines = []
        
        for q in qualities:
            base_q = int(price * q)
            fisher_q = int(base_q * 1.25)
            angler_q = int(base_q * 1.5)
            price_lines.append(f"{base_q}金")
            fisher_lines.append(f"{fisher_q}金")
            angler_lines.append(f"{angler_q}金")

        entry = {
            "名称": display_name,
            "描述": description,
            "价格": "\n".join(price_lines),
            "渔夫职业（+25%）": "\n".join(fisher_lines),
            "垂钓者职业（+50%）": "\n".join(angler_lines),
            "位置": "未知", # Data_Objects doesn't have location
            "时间": "未知",
            "季节": "未知",
            "天气": "未知",
            "图片链接": image_url,
            "来源": SOURCE_NAME_MAP.get(source, "未知"),
            "is_legendary": display_name in legendary_fish_names
        }
        
        # Override with Game Data (Data/Fish)
        if str(item_id) in fish_game_data:
            fd = fish_game_data[str(item_id)]
            
            if fd.get("is_trap"):
                entry["位置"] = fd["location"]
                entry["时间"] = "任意时间"
                entry["季节"] = "任意季节"
                entry["天气"] = "任意天气"
            else:
                entry["时间"] = parse_time(fd["time"])
                entry["季节"] = parse_season(fd["season"])
                entry["天气"] = parse_weather(fd["weather"])
            
        # Override with Location Data (Data/Locations) - Higher Priority
        if str(item_id) in fish_loc_info:
            fl = fish_loc_info[str(item_id)]
            
            # Construct location string based on seasons
            # Also store the raw structured data for frontend
            locs_by_season = fl["locations_by_season"]
            
            # Initialize structured locations
            entry["位置详情"] = {
                "spring": [],
                "summer": [],
                "fall": [],
                "winter": []
            }
            
            # Helper to check if season is valid for this fish (from Data/Fish)
            # If fish_game_data says "summer", but Data/Locations has "all", we should only put it in summer?
            # Or if Data/Locations says "all", does it spawn in winter?
            # Usually Data/Locations spawn logic respects the location's rules.
            # If a location has NO season condition, the fish spawns there regardless of season (unless hardcoded elsewhere).
            # BUT, often "all" in location means it spawns all year.
            
            valid_seasons_game = ["spring", "summer", "fall", "winter"]
            if str(item_id) in fish_game_data:
                game_data_item = fish_game_data[str(item_id)]
                # Trap fish don't have seasons, or are all seasons.
                # Regular fish have "season" key.
                if game_data_item.get("season"):
                    valid_seasons_game = game_data_item["season"].split(' ') # e.g. ["summer", "winter"]
            
            # Populate seasonal lists
            all_locs = locs_by_season.get("all", set())
            
            for season in ["spring", "summer", "fall", "winter"]:
                # Specific locations for this season
                season_specific = locs_by_season.get(season, set())
                
                # Combine specific + all
                # Note: If "all" is present, it applies to this season.
                # However, if fish_game_data restricts it, maybe we should filter?
                # Actually, Data/Locations is the source of truth for spawns. 
                # If Data/Locations says it spawns in Town (no condition), it spawns in Town in Winter even if Data/Fish says Summer.
                # (Data/Fish season is mostly for the encyclopedia).
                # So we should trust Data/Locations.
                
                combined = season_specific.union(all_locs)
                if combined:
                    entry["位置详情"][season] = sorted(list(combined))

            # Update flat "位置" string to be a union of all locations found
            all_found_locs = set()
            for s_locs in locs_by_season.values():
                all_found_locs.update(s_locs)
            
            if all_found_locs:
                entry["位置"] = "、".join(sorted(list(all_found_locs)))
            
            if fl["seasons"]:
                entry["季节"] = parse_season(" ".join(fl["seasons"]))
            
            if fl["weathers"]:
                # If specifically rain or sun is required
                w_list = sorted(list(fl["weathers"]))
                # Logic: if both sun and rain, basically "All Weather".
                # But if "storm" is there, it's specific.
                
                if "sunny" in w_list and "rainy" in w_list and "storm" not in w_list:
                    entry["天气"] = "任意天气"
                else:
                    entry["天气"] = "、".join([parse_weather(w) for w in w_list])
            
            if fl["times"]:
                # If we have location-specific times, they might override general times
                # For now, let's append or replace if vanilla was empty?
                # Actually, Data/Fish usually has the time. Locations might restrict it further?
                # Let's trust Data/Fish for time generally, unless it's missing.
                if entry["时间"] == "未知" or not entry["时间"]:
                     entry["时间"] = ", ".join([parse_time(t) for t in fl["times"]])
        
        # Apply Manual Overrides
        if str(item_id) in overrides:
            fish_override = overrides[str(item_id)]
            for key, val in fish_override.items():
                if key == "位置详情" and isinstance(val, dict):
                    if "位置详情" not in entry:
                        entry["位置详情"] = {}
                    entry["位置详情"].update(val)
                else:
                    entry[key] = val
            print(f"Applied manual override for: {entry['名称']} ({item_id})")

        fish_data_map[source].append(entry)
        count_processed += 1
            
    # Save all
    for source, data in fish_data_map.items():
        if not data:
            continue
        filename = FILE_MAP.get(source)
        if not filename:
             print(f"Warning: No file mapped for source {source}, skipping {len(data)} entries.")
             continue
        save_json(os.path.join(DATA_DIR, filename), data)
        print(f"Saved {filename} with {len(data)} entries.")

    print(f"Processed {count_processed} fish items.")

if __name__ == "__main__":
    main()
