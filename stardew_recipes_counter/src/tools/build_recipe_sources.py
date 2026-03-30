#!/usr/bin/env python3
"""
食谱来源解析脚本
解析 Stardew Valley 食谱的获取来源
使用 SpriteIndex 和中文名匹配
"""

import json
import re
from pathlib import Path

# 路径配置
SRC_DIR = Path(__file__).parent.parent
COOKING_RECIPES_FILE = SRC_DIR / "Data_CookingRecipes.json"
TV_COOKING_CHANNEL_FILE = SRC_DIR / "Data_TV_CookingChannel.json"
MAIL_FILE = SRC_DIR / "Data_mail.json"
FINAL_RECIPES_FILE = SRC_DIR / "final_recipes.json"
OUTPUT_FILE = SRC_DIR / "final_recipes.json"

# NPC 名称中英文映射
NPC_NAMES = {
    "Emily": "艾米丽",
    "Pam": "潘姆",
    "Caroline": "卡洛琳",
    "Jodi": "乔迪",
    "Shane": "谢恩",
    "Demetrius": "德米特里厄斯",
    "Clint": "克林特",
    "Gus": "格斯",
    "Linus": "莱纳斯",
    "Kent": "肯特",
    "Sandy": "桑迪",
    "George": "乔治",
    "Evelyn": "艾芙琳",
    "Lewis": "刘易斯",
    "Pierre": "皮埃尔",
    "Marnie": "玛妮",
    "Robin": "罗宾",
    "Willy": "威利",
    "Leo": "雷欧",
    "Wizard": "法师",
    # SVE NPCs
    "Olivia": "奥利维亚",
    "Victor": "维克多",
    "GuntherSilvian": "冈瑟",
    "Martin": "马丁",
    "Lance": "兰斯",
    "Claire": "克莱尔",
    "Morgan": "摩根",
    "Andy": "安迪",
    "Scarlett": "斯嘉丽",
    "Susan": "苏珊",
    # RSV NPCs
    "Shanice": "莎妮丝",
    "Paula": "宝拉",
    "Blair": "布莱尔",
    "Lorenzo": "洛伦佐",
    "Louie": "路易",
    "Malaya": "马拉亚",
    "Sonny": "桑尼",
    "Sean": "肖恩",
    "Kiarra": "基亚拉",
    "Lola": "萝拉",
    "Kimpoi": "金博",
    "Carmen": "卡门",
    "Naomi": "娜奥米",
    "Irene": "艾琳",
    "Faye": "菲伊",
    "Maive": "梅芙",
    # Other Mod NPCs
    "DialaSBV": "迪亚拉",
    "DeryaSBV": "德里亚",
    "MoonSBV": "阿月",
    "MiyoungSBV": "美英",
    "Eloise": "埃洛伊斯",
    "Rosa": "罗莎",
    "ToriLK": "托里",
    "Jacob": "雅各布",
    "Jessie": "杰西",
    "Beatrice": "比阿特丽斯",
    "JosephineK": "约瑟芬",
    "EdithHart": "伊迪丝",
    "JadeMalic": "杰德",
    "CorwinLK": "科尔温",
    "MichaelHart": "迈克尔",
    "Juliet": "朱丽叶",
    "Jasper": "贾斯珀",
    "CelestineDuboisVMV": "塞莱斯汀",
    "MaddyPellegrinVMV": "玛迪",
    "MoiraDuboisVMV": "莫伊拉",
    "AsterPellegrinVMV": "阿斯特",
    "MariamFortinVMV": "玛丽亚姆",
    "NaveenFaycombeSereneVMV": "纳文",
    "OdalisDuboisVelezVMV": "奥达利斯",
    "Otter.Cambria": "坎布里亚",
}

# 技能名称映射
SKILL_NAMES = {
    "Farming": "耕种",
    "Foraging": "觅食",
    "Fishing": "钓鱼",
    "Mining": "采矿",
    "Combat": "战斗",
    "Luck": "运气",
}


def load_json(file_path):
    """加载 JSON 文件"""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data, file_path):
    """保存 JSON 文件"""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def normalize_source_list(raw_source):
    """将来源字段统一转换为来源对象列表。"""
    if isinstance(raw_source, dict):
        return [raw_source]
    if isinstance(raw_source, list):
        return [item for item in raw_source if isinstance(item, dict)]
    return []


def get_recipe_sources(recipe):
    """读取并合并食谱的所有来源，兼容旧格式和多来源格式。"""
    sources = []

    if isinstance(recipe.get("sources"), list):
        sources.extend(normalize_source_list(recipe.get("sources")))
    else:
        sources.extend(normalize_source_list(recipe.get("source")))

    sources.extend(normalize_source_list(recipe.get("alternate_sources")))

    return sources


def is_meaningful_source(source):
    """判断单个来源是否为有效来源，而不是占位值。"""
    if not isinstance(source, dict):
        return False

    source_type = source.get("type")
    description = (source.get("description") or "").strip()
    details = source.get("details")

    if source_type and source_type not in {"other", "unknown"}:
        return True

    if description and description not in {"其他途径", "未知来源"}:
        return True

    if isinstance(details, dict) and details:
        return True

    return False


def has_meaningful_source(recipe):
    """判断食谱是否已有手动维护的有效来源信息。"""
    return any(is_meaningful_source(source) for source in get_recipe_sources(recipe))


def get_meaningful_recipe_sources(recipe):
    """获取食谱中所有有效来源。"""
    return [source for source in get_recipe_sources(recipe) if is_meaningful_source(source)]


def same_source(left, right):
    """判断两个来源对象是否表示同一来源。"""
    if not isinstance(left, dict) or not isinstance(right, dict):
        return False

    return (
        left.get("type") == right.get("type")
        and left.get("description") == right.get("description")
        and (left.get("details") or {}) == (right.get("details") or {})
    )


def same_source_identity(left, right):
    """判断两个来源是否是同一来源（忽略 details，便于合并补充字段）。"""
    if not isinstance(left, dict) or not isinstance(right, dict):
        return False

    return (
        left.get("type") == right.get("type")
        and left.get("description") == right.get("description")
    )


def set_recipe_sources(recipe, primary_source, extra_sources=None):
    """将来源写回为兼容格式：source + alternate_sources。"""
    recipe["source"] = primary_source

    if extra_sources:
        recipe["alternate_sources"] = extra_sources
    else:
        recipe.pop("alternate_sources", None)

    recipe.pop("sources", None)


def parse_tv_cooking_channel(tv_data):
    """解析电视烹饪频道数据，返回 {食谱英文名: 播出集数} 映射"""
    tv_recipes = {}
    for episode_num, content in tv_data.items():
        # 格式: "食谱名/描述..."
        parts = content.split("/")
        if len(parts) >= 1:
            recipe_name = parts[0].strip()
            tv_recipes[recipe_name] = int(episode_num)
    return tv_recipes


def get_tv_air_date(episode_num):
    """根据集数计算播出日期（女王的酱汁每周日播出）"""
    # 第1集在第1年春季第7天播出，之后每周一集
    # 每季28天，每年4季
    year = ((episode_num - 1) * 7) // (28 * 4) + 1
    day_of_year = ((episode_num - 1) * 7) % (28 * 4) + 7
    
    season_num = day_of_year // 28
    day = day_of_year % 28
    if day == 0:
        day = 28
        season_num -= 1
    
    seasons = ["春", "夏", "秋", "冬"]
    season = seasons[season_num % 4]
    
    return f"第{year}年{season}季第{day}天"


def parse_source_condition(condition_str, recipe_name, tv_recipes):
    """
    解析食谱来源条件字符串
    返回: {
        "type": "来源类型",
        "description": "中文描述",
        "details": {...}  # 额外信息
    }
    """
    if not condition_str or condition_str.strip() == "":
        return {
            "type": "unknown",
            "description": "未知来源",
            "details": {}
        }
    
    condition = condition_str.strip()
    
    # 初始拥有
    if condition == "default":
        return {
            "type": "default",
            "description": "初始拥有",
            "details": {}
        }
    
    # 电视节目 (l 100 表示不可能达到的等级，实际是电视)
    if condition == "l 100":
        # 尝试匹配电视节目
        if recipe_name in tv_recipes:
            episode = tv_recipes[recipe_name]
            air_date = get_tv_air_date(episode)
            return {
                "type": "tv",
                "description": f"电视「女王的酱汁」第{episode}集",
                "details": {
                    "episode": episode,
                    "air_date": air_date
                }
            }
        return {
            "type": "tv",
            "description": "电视节目「女王的酱汁」",
            "details": {}
        }
    
    # 玩家等级
    level_match = re.match(r"l (\d+)", condition)
    if level_match:
        level = int(level_match.group(1))
        if level < 100:  # 正常等级
            return {
                "type": "level",
                "description": f"玩家等级 {level} 级",
                "details": {"level": level}
            }
    
    # NPC 好感度
    friendship_match = re.match(r"f ([^\s]+) (\d+)", condition)
    if friendship_match:
        npc_id = friendship_match.group(1)
        hearts = int(friendship_match.group(2))
        npc_name = NPC_NAMES.get(npc_id, npc_id)
        return {
            "type": "friendship",
            "description": f"{npc_name} {hearts}❤",
            "details": {"npc": npc_id, "npc_cn": npc_name, "hearts": hearts}
        }
    
    # 技能等级
    skill_match = re.match(r"s (\w+) (\d+)", condition)
    if skill_match:
        skill_id = skill_match.group(1)
        level = int(skill_match.group(2))
        skill_name = SKILL_NAMES.get(skill_id, skill_id)
        return {
            "type": "skill",
            "description": f"{skill_name}等级 {level}",
            "details": {"skill": skill_id, "skill_cn": skill_name, "level": level}
        }
    
    # 事件触发
    event_match = re.match(r"e (.+)", condition)
    if event_match:
        event_id = event_match.group(1)
        return {
            "type": "event",
            "description": "事件触发",
            "details": {"event_id": event_id}
        }
    
    # null 来源
    if condition == "null" or condition == "none" or condition == "false":
        return {
            "type": "other",
            "description": "其他途径",
            "details": {"original": condition}
        }
    
    # 季节日期条件
    season_match = re.match(r"SEASON_DAY (\w+) (\d+)", condition)
    if season_match:
        season = season_match.group(1)
        day = int(season_match.group(2))
        season_cn = {"spring": "春", "summer": "夏", "fall": "秋", "winter": "冬"}.get(season, season)
        return {
            "type": "seasonal",
            "description": f"{season_cn}季第{day}天",
            "details": {"season": season, "day": day}
        }
    
    # 农舍升级条件
    if "FARMHOUSE_UPGRADE" in condition:
        return {
            "type": "upgrade",
            "description": "农舍升级后获得",
            "details": {"original": condition}
        }
    
    # 其他未知条件
    return {
        "type": "other",
        "description": "其他途径",
        "details": {"original": condition}
    }


def calculate_sprite_index(x, y, texture):
    """根据坐标和纹理计算 SpriteIndex"""
    # 原版 springobjects 每行24个，每个16x16像素
    if "springobjects" in texture.lower():
        return (y // 16) * 24 + (x // 16)
    # Mod 纹理可能使用不同的布局，返回 None
    return None


def main():
    print("=" * 50)
    print("食谱来源解析脚本 v2")
    print("=" * 50)
    
    # 加载数据
    print("\n[1/5] 加载数据文件...")
    cooking_recipes = load_json(COOKING_RECIPES_FILE)
    tv_data = load_json(TV_COOKING_CHANNEL_FILE)
    final_recipes = load_json(FINAL_RECIPES_FILE)
    
    print(f"  - 烹饪食谱: {len(cooking_recipes)} 个")
    print(f"  - 电视节目: {len(tv_data)} 集")
    print(f"  - 现有食谱数据: {len(final_recipes)} 个")
    
    # 解析电视节目
    print("\n[2/5] 解析电视节目数据...")
    tv_recipes = parse_tv_cooking_channel(tv_data)
    print(f"  - 电视食谱: {len(tv_recipes)} 个")
    
    # 加载翻译文件
    print("\n[2.5/5] 加载翻译文件...")
    try:
        with open(SRC_DIR / "Strings_Objects.json", "r", encoding="utf-8") as f:
            strings_objects = json.load(f)
        # 建立中文名到英文ID的映射
        cn_to_en_id = {}
        en_id_to_cn = {}
        for key, value in strings_objects.items():
            if key.endswith("_Name"):
                item_id = key[:-5]  # 去掉 _Name 后缀
                cn_to_en_id[value] = item_id
                en_id_to_cn[item_id] = value
        print(f"  - 翻译条目: {len(cn_to_en_id)} 个")
    except Exception as e:
        print(f"  - 翻译文件加载失败: {e}")
        cn_to_en_id = {}
        en_id_to_cn = {}
    
    # 创建食谱来源映射 (按物品ID和中文名)
    print("\n[3/5] 建立食谱映射...")
    
    # 按物品ID映射
    id_to_source = {}
    # 按中文名映射
    cn_to_source = {}
    # 按英文名映射
    en_to_source = {}
    # 按物品ID（不带空格）映射
    normalized_id_to_source = {}
    
    for eng_name, recipe_data in cooking_recipes.items():
        parts = recipe_data.split("/")
        if len(parts) >= 4:
            item_id = parts[2]  # 物品ID
            condition = parts[3]  # 来源条件
            cn_name = parts[4] if len(parts) >= 5 and parts[4] else None
            
            source = parse_source_condition(condition, eng_name, tv_recipes)
            
            # 添加英文名到source
            source["eng_name"] = eng_name
            
            # 按物品ID存储
            id_to_source[item_id] = source
            
            # 按英文名存储
            en_to_source[eng_name] = source
            
            # 按英文名（去空格）存储
            normalized_name = eng_name.replace(" ", "")
            normalized_id_to_source[normalized_name] = source
            
            # 按中文名存储 (如果有)
            if cn_name:
                cn_to_source[cn_name] = source
    
    print(f"  - 按ID映射: {len(id_to_source)} 个")
    print(f"  - 按中文名映射: {len(cn_to_source)} 个")
    print(f"  - 按英文名映射: {len(en_to_source)} 个")
    
    # 更新 final_recipes.json
    print("\n[4/5] 更新食谱数据...")
    updated_count = 0
    preserved_count = 0
    not_found = []
    source_stats = {}
    
    for recipe in final_recipes:
        recipe_name = recipe.get("name", "")
        x = recipe.get("x", 0)
        y = recipe.get("y", 0)
        texture = recipe.get("texture", "")
        
        source = None
        match_method = ""
        
        # 方法1: 通过中文名匹配
        if recipe_name in cn_to_source:
            source = cn_to_source[recipe_name]
            match_method = "中文名"
        
        # 方法2: 通过英文名匹配
        if not source and recipe_name in en_to_source:
            source = en_to_source[recipe_name]
            match_method = "英文名"
        
        # 方法3: 通过 SpriteIndex 匹配 (仅限原版纹理)
        if not source and "springobjects" in texture.lower():
            sprite_index = calculate_sprite_index(x, y, texture)
            if sprite_index is not None and str(sprite_index) in id_to_source:
                source = id_to_source[str(sprite_index)]
                match_method = f"SpriteIndex({sprite_index})"
        
        # 方法4: 通过翻译文件匹配 (中文名 -> 英文ID -> 去空格后匹配)
        if not source and recipe_name in cn_to_en_id:
            en_id = cn_to_en_id[recipe_name]
            # 尝试直接匹配
            if en_id in normalized_id_to_source:
                source = normalized_id_to_source[en_id]
                match_method = f"Strings({en_id})"
        
        # 方法5: 尝试模糊匹配 Mod 物品ID
        if not source:
            for item_id, src in id_to_source.items():
                # 检查是否是 Mod 物品ID (包含点号或下划线)
                if "." in item_id or "_" in item_id:
                    # 尝试从物品ID中提取名称进行匹配
                    id_parts = item_id.replace(".", "_").split("_")
                    for part in id_parts:
                        if part.lower() in recipe_name.lower() or recipe_name.lower() in part.lower():
                            source = src
                            match_method = f"ModID({item_id})"
                            break
                if source:
                    break
        
        if source:
            # 复制 source 避免修改原始数据
            auto_source = {
                "type": source["type"],
                "description": source["description"],
                "details": source.get("details", {})
            }
            existing_sources = get_meaningful_recipe_sources(recipe)
            matching_existing_source = next(
                (existing for existing in existing_sources if same_source_identity(existing, auto_source)),
                None
            )
            existing_details = matching_existing_source.get("details", {}) if matching_existing_source else {}
            auto_details = auto_source.get("details", {})
            auto_source["details"] = {
                **(existing_details if isinstance(existing_details, dict) else {}),
                **(auto_details if isinstance(auto_details, dict) else {}),
            }
            alternate_sources = [
                existing for existing in existing_sources
                if isinstance(existing, dict) and not same_source_identity(existing, auto_source)
            ]
            set_recipe_sources(recipe, auto_source, alternate_sources)
            updated_count += 1
            
            # 统计
            source_type = auto_source["type"]
            source_stats[source_type] = source_stats.get(source_type, 0) + 1
        else:
            if has_meaningful_source(recipe):
                preserved_count += 1
                existing_sources = get_meaningful_recipe_sources(recipe)
                primary_source = existing_sources[0]
                alternate_sources = existing_sources[1:]
                set_recipe_sources(recipe, primary_source, alternate_sources)
                source_type = primary_source.get("type") or "manual"
                source_stats[source_type] = source_stats.get(source_type, 0) + 1
            else:
                # 仅在原本没有有效来源时，回退到占位值
                set_recipe_sources(recipe, {
                    "type": "other",
                    "description": "其他途径",
                    "details": {}
                })
                not_found.append(recipe_name)
                source_stats["other"] = source_stats.get("other", 0) + 1
    
    print(f"  - 成功匹配: {updated_count} 个")
    print(f"  - 保留现有来源: {preserved_count} 个")
    print(f"  - 未匹配: {len(not_found)} 个")
    
    print("\n  来源类型统计:")
    for source_type, count in sorted(source_stats.items(), key=lambda x: -x[1]):
        print(f"    - {source_type}: {count} 个")
    
    if not_found and len(not_found) <= 30:
        print("\n  未匹配的食谱:")
        for name in not_found[:30]:
            print(f"    - {name}")
    elif not_found:
        print(f"\n  未匹配的食谱: 共 {len(not_found)} 个 (仅显示前30个)")
        for name in not_found[:30]:
            print(f"    - {name}")
    
    # 保存更新后的数据
    print("\n[5/5] 保存数据...")
    save_json(final_recipes, OUTPUT_FILE)
    print(f"  已保存到: {OUTPUT_FILE}")
    
    print("\n" + "=" * 50)
    print("完成!")
    print("=" * 50)


if __name__ == "__main__":
    main()
