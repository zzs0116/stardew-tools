#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
星露谷制作配方数据处理脚本 (修复版)
增加对 Big Craftables 的支持
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional


class CraftingDataProcessor:
    """制作配方数据处理器"""
    
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        self.recipes_raw = {}
        self.objects_data = {}
        self.big_craftables_data = {}
        self.strings_objects = {}
        self.manual_overrides = {}
        self.output_data = []
        
    def load_data(self):
        """加载所有数据文件"""
        print("📖 正在加载数据文件...")
        
        # 加载配方数据
        with open(self.data_dir / "Data_CraftingRecipes.json", "r", encoding="utf-8") as f:
            self.recipes_raw = json.load(f)
        print(f"   ✓ 加载了 {len(self.recipes_raw)} 个配方")
        
        # 加载物品数据
        with open(self.data_dir / "Data_Objects.json", "r", encoding="utf-8") as f:
            self.objects_data = json.load(f)
        print(f"   ✓ 加载了 {len(self.objects_data)} 个普通物品")
        
        # 加载 Big Craftables 数据（如果存在）
        big_craftables_file = self.data_dir / "Data_BigCraftables.json"
        if big_craftables_file.exists():
            with open(big_craftables_file, "r", encoding="utf-8") as f:
                self.big_craftables_data = json.load(f)
            print(f"   ✓ 加载了 {len(self.big_craftables_data)} 个大型可制作物")
        else:
            print(f"   ⚠ 未找到 Big Craftables 数据文件，部分配方可能显示不正确")
            print(f"   提示：请运行 SMAPI 命令获取该文件")
        
        # 加载中文翻译
        with open(self.data_dir / "Strings_Objects.json", "r", encoding="utf-8") as f:
            self.strings_objects = json.load(f)
        print(f"   ✓ 加载了 {len(self.strings_objects)} 条物品翻译")
        
        # 加载 BigCraftables 翻译
        big_craftables_strings_file = self.data_dir / "Strings_BigCraftables.json"
        if big_craftables_strings_file.exists():
            with open(big_craftables_strings_file, "r", encoding="utf-8") as f:
                big_craftables_strings = json.load(f)
                # 将 BigCraftables 翻译合并到 strings_objects 中
                self.strings_objects.update(big_craftables_strings)
            print(f"   ✓ 加载了 {len(big_craftables_strings)} 条大型可制作物翻译")
        else:
            print(f"   ⚠ 未找到 BigCraftables 翻译文件")
        
        # 加载手动覆盖配置
        overrides_file = Path("manual_overrides.json")
        if overrides_file.exists():
            with open(overrides_file, "r", encoding="utf-8") as f:
                self.manual_overrides = json.load(f)
                # 过滤掉以 _ 开头的说明性字段
                self.manual_overrides = {k: v for k, v in self.manual_overrides.items() if not k.startswith("_")}
            if self.manual_overrides:
                print(f"   ✓ 加载了 {len(self.manual_overrides)} 条手动覆盖配置")
    
    def get_cn_name(self, key: str) -> str:
        """
        获取中文名称
        key格式: [LocalizedText Strings\\Objects:ItemName]
        """
        if not key or not key.startswith("[LocalizedText"):
            return key
        
        # 提取实际的 key: Strings\\Objects:ItemName -> ItemName
        match = re.search(r':(\w+)]', key)
        if match:
            item_key = match.group(1)
            return self.strings_objects.get(item_key, key)
        return key
    
    def get_object_info(self, item_id: str, is_big_craftable: bool = False) -> Dict[str, str]:
        """
        获取物品信息
        is_big_craftable: 是否是大型可制作物
        """
        # 处理 (BC) 或 (O) 前缀
        clean_id = item_id.replace("(BC)", "").replace("(O)", "").strip()
        
        # 根据类型选择数据源
        if is_big_craftable and self.big_craftables_data:
            item_data = self.big_craftables_data.get(clean_id, {})
        else:
            item_data = self.objects_data.get(clean_id, {})
        
        # 如果在指定数据源中找不到，尝试另一个数据源
        if not item_data:
            if is_big_craftable:
                item_data = self.objects_data.get(clean_id, {})
            elif self.big_craftables_data:
                item_data = self.big_craftables_data.get(clean_id, {})
        
        return {
            "id": item_id,
            "名称": self.get_cn_name(item_data.get("DisplayName", "")),
            "名称_EN": item_data.get("Name", ""),
            "描述": self.get_cn_name(item_data.get("Description", "")),
            "价格": item_data.get("Price", 0),
            "类型": item_data.get("Type", ""),
        }
    
    def parse_ingredients(self, ingredients_str: str) -> List[Dict[str, Any]]:
        """
        解析配方材料
        """
        parts = ingredients_str.split("/")
        if not parts:
            return []
        
        ingredients_part = parts[0].strip()
        tokens = ingredients_part.split()
        
        ingredients = []
        i = 0
        while i < len(tokens):
            item_id = tokens[i]
            quantity = int(tokens[i + 1]) if i + 1 < len(tokens) else 1
            
            # 检查是否是 BigCraftable (有 (BC) 前缀)
            is_bc = item_id.startswith("(BC)")
            item_info = self.get_object_info(item_id, is_big_craftable=is_bc)
            ingredients.append({
                "id": item_id,
                "名称": item_info["名称"],
                "数量": quantity
            })
            
            i += 2
        
        return ingredients
    
    def parse_unlock_condition(self, condition_str: str) -> str:
        """解析解锁条件"""
        condition_str = condition_str.strip()
        
        if condition_str == "default":
            return "默认解锁"
        elif condition_str == "null" or condition_str == "none":
            return "待补充"
        elif condition_str.startswith("s "):
            parts = condition_str.split()
            if len(parts) >= 3:
                skill_map = {
                    "Farming": "耕种",
                    "Fishing": "钓鱼",
                    "Foraging": "采集",
                    "Mining": "采矿",
                    "Combat": "战斗"
                }
                skill = skill_map.get(parts[1], parts[1])
                level = parts[2]
                return f"{skill}技能 Lv.{level}"
        elif condition_str.startswith("f "):
            parts = condition_str.split()
            if len(parts) >= 3:
                npc = parts[1]
                hearts = parts[2]
                return f"与 {npc} 好感度 {hearts} 颗心"
        elif condition_str.startswith("l "):
            parts = condition_str.split()
            if len(parts) >= 2:
                level = parts[1]
                return f"矿井层数 {level}"
        elif condition_str.startswith("e "):
            return "特定活动/任务"
        else:
            # 处理没有前缀的技能条件（MOD配方可能直接使用 "Farming 4" 格式）
            parts = condition_str.split()
            if len(parts) >= 2:
                skill_map = {
                    "Farming": "耕种",
                    "Fishing": "钓鱼",
                    "Foraging": "采集",
                    "Mining": "采矿",
                    "Combat": "战斗"
                }
                if parts[0] in skill_map:
                    skill = skill_map[parts[0]]
                    level = parts[1]
                    return f"{skill}技能 Lv.{level}"
        
        return condition_str
    
    def parse_recipe(self, recipe_name: str, recipe_data: str) -> Dict[str, Any]:
        """
        解析单个配方
        格式: "材料/类型/产物ID 数量/是否big/解锁条件/显示名称"
        """
        parts = recipe_data.split("/")
        
        # 解析材料
        ingredients = self.parse_ingredients(recipe_data)
        
        # 解析产物
        output_id = parts[2] if len(parts) > 2 else ""
        output_quantity = 1
        if " " in output_id:
            output_parts = output_id.split()
            output_id = output_parts[0]
            output_quantity = int(output_parts[1]) if len(output_parts) > 1 else 1
        
        # **关键修复：检查第四个字段判断是否是 BigCraftable**
        is_big_craftable = parts[3].lower() == "true" if len(parts) > 3 else False
        
        output_info = self.get_object_info(output_id, is_big_craftable=is_big_craftable)
        
        # 解析类型
        category = parts[1] if len(parts) > 1 else ""
        category_map = {
            "Field": "户外",
            "Home": "室内",
            "Ring": "戒指"
        }
        category_cn = category_map.get(category, category)
        
        # 解析解锁条件
        unlock_condition = parts[4] if len(parts) > 4 else "default"
        unlock_cn = self.parse_unlock_condition(unlock_condition)
        
        # 自定义显示名称
        custom_name = None
        if len(parts) > 5 and parts[5]:
            custom_name = parts[5]
            if custom_name.startswith("[LocalizedText"):
                match = re.search(r':CraftingRecipe_(\w+)]', custom_name)
                if match:
                    key = f"CraftingRecipe_{match.group(1)}"
                    custom_name = self.strings_objects.get(key, None)
        
        # 判断来源（传入完整的配方数据以便检查材料和产物ID）
        source = self.determine_source(recipe_name, recipe_data, unlock_cn)
        
        # 图片路径（BigCraftables 使用不同的路径）
        image_path = f"./images/craftables/{output_id}.png" if is_big_craftable else f"./images/objects/{output_id}.png"
        
        # 配方显示名称：优先使用自定义名称，其次使用产物名称，最后使用英文配方名
        display_name = custom_name if custom_name else (output_info["名称"] if output_info["名称"] else recipe_name)
        
        recipe_obj = {
            "名称": display_name,
            "名称_EN": recipe_name,
            "描述": output_info.get("描述", ""),
            "材料": ingredients,
            "产物": {
                "id": output_id,
                "名称": output_info["名称"],
                "数量": output_quantity,
                "是大型可制作物": is_big_craftable
            },
            "分类": category_cn,
            "解锁条件": unlock_cn,
            "解锁条件描述": "",  # 默认为空，可通过 manual_overrides 覆盖
            "来源": source,
            "图片链接": image_path
        }
        
        # 应用手动覆盖
        if recipe_name in self.manual_overrides:
            overrides = self.manual_overrides[recipe_name]
            for key, value in overrides.items():
                if key in recipe_obj:
                    recipe_obj[key] = value
        
        return recipe_obj
    
    def determine_source(self, recipe_name: str, recipe_data: str, unlock_condition: str) -> str:
        """
        根据配方名称、配方数据和解锁条件判断来源
        优先根据配方数据内容（材料ID、产物ID等）判断，其次根据配方名称
        """
        # 将配方名称和数据合并为完整文本进行检查
        full_text = f"{recipe_name} {recipe_data}"
        
        # 检查 SVE (优先级最高，因为经常被误判)
        if "FlashShifter" in full_text or "StardewValleyExpandedCP" in full_text or "SVE" in unlock_condition:
            return "SVE"
        
        # 检查其他 MOD
        if "Rafseazz" in full_text or "RSVCP" in full_text:
            return "里奇赛德村"
        elif "skellady" in full_text or "SBVCP" in full_text:
            return "阳莓村"
        # 东斯卡普（包含 Ancient Forest 和 Depths of the Night）
        elif "EastScarp" in full_text or "Lemurkat" in full_text or "TenebrousNova" in full_text or "DN.SnS" in full_text:
            return "东斯卡普"
        elif "Lumisteria" in full_text or "MtVapius" in full_text:
            return "雾呜山"
        elif "MNF" in full_text:
            return "更多的鱼"
        elif "Cornucopia" in full_text:
            return "Cornucopia（聚宝盆）"
        elif "DTZ" in full_text:
            return "祖祖城"
        elif "leclair" in full_text:
            return "魔法工作台"
        
        # 默认为原版（包括解锁条件为"默认解锁"的）
        return "原版"
    
    def process_all_recipes(self):
        """处理所有配方"""
        print(f"\n🔄 正在处理配方数据...")
        
        for recipe_name, recipe_data in self.recipes_raw.items():
            try:
                recipe_obj = self.parse_recipe(recipe_name, recipe_data)
                self.output_data.append(recipe_obj)
            except Exception as e:
                print(f"   ⚠ 处理配方 '{recipe_name}' 时出错: {e}")
        
        print(f"   ✓ 成功处理 {len(self.output_data)} 个配方")
    
    def save_output(self, output_file: str = "data/crafting_data.json"):
        """保存处理后的数据"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.output_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 数据已保存到: {output_path}")
        print(f"   共 {len(self.output_data)} 个配方")
    
    def run(self):
        """执行完整的数据处理流程"""
        self.load_data()
        self.process_all_recipes()
        self.save_output()


if __name__ == "__main__":
    processor = CraftingDataProcessor()
    processor.run()
