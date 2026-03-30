import json
import os
from PIL import Image

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def p(*parts):
    return os.path.join(BASE_DIR, *parts)

print("=" * 60)
print("🔍 星露谷食谱项目诊断报告")
print("=" * 60)

# 1. 检查数据文件
with open(p('final_recipes.json'), 'r', encoding='utf-8') as f:
    recipes = json.load(f)

print(f"\n📊 数据统计:")
print(f"   ✓ 食谱总数: {len(recipes)}")

# 2. 检查异常宽度的贴图
print(f"\n🖼️  贴图资源检查:")
assets_dir = p('assets')
abnormal_widths = []
for fname in os.listdir(assets_dir):
    if fname.endswith('.png'):
        try:
            with Image.open(os.path.join(assets_dir, fname)) as img:
                w, h = img.size
                if w % 16 != 0:
                    abnormal_widths.append((fname, w, h))
        except:
            pass

if abnormal_widths:
    print(f"   ⚠️  发现 {len(abnormal_widths)} 个宽度非 16 倍数的贴图:")
    for fname, w, h in abnormal_widths:
        print(f"      - {fname}: {w}x{h} (列数: {w//16}, 余数: {w%16})")
else:
    print(f"   ✓ 所有贴图宽度均为 16 的倍数")

# 3. 检查未翻译项
print(f"\n🌐 翻译完整性:")
untranslated_recipes = [r for r in recipes if 'Unknown' in r['name'] or '[' in r['name']]
untranslated_ings = []
for r in recipes:
    for ing in r['ingredients']:
        if 'Unknown' in ing['name'] or '[' in ing['name']:
            untranslated_ings.append((r['name'], ing['name']))

if untranslated_recipes:
    print(f"   ⚠️  {len(untranslated_recipes)} 个未翻译的食谱:")
    for r in untranslated_recipes[:5]:
        print(f"      - {r['name']}")
else:
    print(f"   ✓ 所有食谱名称已翻译")

if untranslated_ings:
    print(f"   ⚠️  {len(untranslated_ings)} 个未翻译的原料:")
    for recipe, ing in untranslated_ings[:5]:
        print(f"      - {recipe} 需要 {ing}")
else:
    print(f"   ✓ 所有原料名称已翻译")

# 4. 检查坐标计算
print(f"\n📐 坐标计算检查:")
coord_issues = []
for r in recipes:
    for item in [r] + r['ingredients']:
        if item['sw'] == 0:
            coord_issues.append(f"{item['name']} - sw=0")
        elif item['x'] < 0 or item['y'] < 0:
            coord_issues.append(f"{item['name']} - 负坐标 x={item['x']}, y={item['y']}")

if coord_issues:
    print(f"   ⚠️  {len(coord_issues)} 个坐标异常:")
    for issue in coord_issues[:5]:
        print(f"      - {issue}")
else:
    print(f"   ✓ 所有坐标计算正常")

# 5. 检查分类图标映射
print(f"\n🏷️  分类图标统计:")
category_items = {}
for r in recipes:
    for ing in r['ingredients']:
        if ing['name'].startswith('任意'):
            category_items[ing['name']] = category_items.get(ing['name'], 0) + 1

if category_items:
    print(f"   分类原料使用频率:")
    for cat, count in sorted(category_items.items(), key=lambda x: -x[1])[:5]:
        print(f"      - {cat}: {count} 次")

# 6. 贴图文件统计
print(f"\n📦 资源文件统计:")
texture_usage = {}
for r in recipes:
    for item in [r] + r['ingredients']:
        tex = item['texture']
        texture_usage[tex] = texture_usage.get(tex, 0) + 1

print(f"   使用的贴图文件总数: {len(texture_usage)}")
print(f"   最常用的贴图:")
for tex, count in sorted(texture_usage.items(), key=lambda x: -x[1])[:5]:
    print(f"      - {tex}: {count} 次")

print("\n" + "=" * 60)
print("✨ 诊断完成!")
print("=" * 60)
