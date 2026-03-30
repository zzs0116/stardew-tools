"""导出食谱为 Markdown 表格格式"""
import json
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def p(*parts):
    return os.path.join(BASE_DIR, *parts)

print("# 🍲 星露谷食谱完整列表\n")
print(f"**生成时间：** 2026-01-19\n")

with open(p('final_recipes.json'), 'r', encoding='utf-8') as f:
    recipes = json.load(f)

# 按 Mod 分组
mod_groups = {}
for r in recipes:
    if 'Mods_' in r['texture']:
        mod_name = r['texture'].split('_')[1].split('.')[0]
    else:
        mod_name = 'Vanilla'
    
    if mod_name not in mod_groups:
        mod_groups[mod_name] = []
    mod_groups[mod_name].append(r)

# 输出统计
print(f"**总计：** {len(recipes)} 个食谱\n")
print("## 📊 Mod 分布\n")
for mod, items in sorted(mod_groups.items(), key=lambda x: -len(x[1])):
    print(f"- **{mod}**: {len(items)} 个")
print("\n---\n")

# 输出详细列表
for mod, items in sorted(mod_groups.items(), key=lambda x: -len(x[1])):
    print(f"\n## {mod} ({len(items)} 个)\n")
    print("| 食谱名称 | 所需原料 |")
    print("|---------|---------|")
    
    for r in sorted(items, key=lambda x: x['name']):
        ingredients = ' + '.join([f"{ing['name']}×{ing['count']}" for ing in r['ingredients']])
        print(f"| {r['name']} | {ingredients} |")

print("\n---\n")
print("**生成工具：** stardew_recipes_counter")
