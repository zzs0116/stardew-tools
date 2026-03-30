import json
import os
import re
from PIL import Image

# ================= 路径配置 =================
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
OBJS_PATH = os.path.join(BASE_DIR, "Data_Objects.json")
RECIPES_PATH = os.path.join(BASE_DIR, "Data_CookingRecipes.json")
OUTPUT_PATH = os.path.join(BASE_DIR, "final_recipes.json")

# 分类显示名称映射
CATEGORY_MAP = {
    "-1": "任意", "-2": "宝石", "-4": "任意鱼类", "-5": "任意鸡蛋", 
    "-6": "任意牛奶", "-7": "烹饪", "-12": "矿物", "-15": "金属资源", 
    "-16": "建筑资源", "-20": "垃圾", "-21": "任意野味", "-22": "古物", 
    "-75": "任意蔬菜", "-79": "任意水果", "-80": "任意花朵"
}

# 图标借用映射
CATEGORY_ICON_MAP = {
    "-4": "136", "-5": "176", "-6": "184", "-75": "24", "-79": "190",
}

IMG_CACHE = {}

def get_img_meta(tex_path):
    """获取贴图元数据，防止除以零"""
    clean_path = re.sub(r'[\\/]', '_', tex_path)
    file_name = f"{clean_path}.png"
    
    if file_name in IMG_CACHE:
        return IMG_CACHE[file_name]
    
    full_path = os.path.join(ASSETS_DIR, file_name)
    if os.path.exists(full_path):
        try:
            with Image.open(full_path) as img:
                w, _ = img.size
                # 核心修复：确保列数至少为 1，防止除以零
                cols = max(1, w // 16)
                meta = {"file": file_name, "width": w, "cols": cols}
                IMG_CACHE[file_name] = meta
                return meta
        except: pass
    
    return {"file": "Maps_springobjects.png", "width": 384, "cols": 24}

def build_recipe_database():
    if not os.path.exists(OBJS_PATH) or not os.path.exists(RECIPES_PATH):
        print(f"❌ 错误：路径不存在 {BASE_DIR}")
        return

    with open(OBJS_PATH, 'r', encoding='utf-8') as f:
        objs_data = json.load(f)
        if "Fields" in objs_data: objs_data = objs_data["Fields"]

    with open(RECIPES_PATH, 'r', encoding='utf-8') as f:
        recipes_raw = json.load(f)
        if "Fields" in recipes_raw: recipes_raw = recipes_raw["Fields"]

    # 加载本地化翻译
    translation_db = {}
    for filename in os.listdir(BASE_DIR):
        if filename.startswith("Strings_") and filename.endswith(".json"):
            asset_tag = filename.replace(".json", "").replace("Strings_", "Strings/").replace("_", "/")
            try:
                with open(os.path.join(BASE_DIR, filename), 'r', encoding='utf-8') as f:
                    content = json.load(f)
                    for k, v in content.items():
                        translation_db[f"{asset_tag}:{k}"] = v
            except: pass

    def get_visual(item_id):
        tid = str(item_id)
        if tid in CATEGORY_ICON_MAP: tid = CATEGORY_ICON_MAP[tid]
        
        info = objs_data.get(tid, {})
        tex_path = info.get("Texture") or "Maps/springobjects"
        meta = get_img_meta(tex_path)
        
        # 1.6 优先使用 SpriteIndex
        idx = info.get("SpriteIndex")
        if idx is None: idx = info.get("ParentSheetIndex")
        if idx is None:
            idx = int(tid) if tid.isdigit() else 0
        
        # 记录逻辑宽度以进行前端缩放
        return {
            "texture": meta["file"],
            "x": (int(idx) % meta["cols"]) * 16,
            "y": (int(idx) // meta["cols"]) * 16,
            "sw": meta["width"]
        }

    def get_name(item_id, raw):
        if str(item_id) in CATEGORY_MAP: return CATEGORY_MAP[str(item_id)]
        if not raw: return f"Unknown({item_id})"
        match = re.search(r'\[LocalizedText (.*?):(.*?)\]', str(raw))
        if match:
            path = match.group(1).replace('\\', '/')
            key = match.group(2)
            return translation_db.get(f"{path}:{key}", raw)
        return raw

    processed = []
    print("🚀 正在重新计算坐标（已修复除以零错误）...")

    for name, data in recipes_raw.items():
        parts = data.split('/')
        if len(parts) < 3: continue
        
        out_id = parts[2].split(' ')[0]
        obj_info = objs_data.get(out_id, {})
        
        item = {
            "name": get_name(out_id, parts[4] if len(parts) > 4 and parts[4] else obj_info.get("DisplayName", name)),
            **get_visual(out_id),
            "ingredients": []
        }
        
        ing_raw = parts[0].split(' ')
        for i in range(0, len(ing_raw), 2):
            if i + 1 >= len(ing_raw): break
            ing_id = ing_raw[i]
            ing_obj = objs_data.get(ing_id, {})
            item["ingredients"].append({
                "name": get_name(ing_id, ing_obj.get("DisplayName")),
                "count": ing_raw[i+1],
                **get_visual(ing_id)
            })
        processed.append(item)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(processed, f, ensure_ascii=False, indent=2)
    print(f"✨ 数据库已更新：{OUTPUT_PATH}")

if __name__ == "__main__":
    build_recipe_database()
