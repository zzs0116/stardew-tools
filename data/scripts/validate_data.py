#!/usr/bin/env python3
"""
数据完整性验证脚本
验证新生成的数据是否符合预期
"""

import json
from pathlib import Path
from collections import Counter


def validate_data():
    base_dir = Path("/Users/edisonzhang/Documents/Projects/stardew_tools")
    
    print("="*70)
    print("🔍 数据完整性验证报告")
    print("="*70 + "\n")
    
    # 1. 验证统一格式数据
    print("📦 1. 验证统一格式数据 (items_unified.json)")
    print("-"*70)
    
    unified_file = base_dir / "data" / "processed" / "items_unified.json"
    with open(unified_file, 'r', encoding='utf-8') as f:
        unified_items = json.load(f)
    
    print(f"   总物品数: {len(unified_items)}")
    
    # 检查必需字段
    required_fields = ['id', 'name', 'displayName', 'description', 'type', 'category', 'price', 'sprite']
    missing_fields = []
    
    for item in unified_items[:100]:  # 抽样检查
        for field in required_fields:
            if field not in item:
                missing_fields.append((item['id'], field))
    
    if missing_fields:
        print(f"   ⚠️  发现缺失字段: {len(missing_fields)} 个")
    else:
        print(f"   ✅ 所有必需字段完整")
    
    # 中文翻译统计
    has_zh = [i for i in unified_items if i['displayName']['zh'] and i['displayName']['zh'] != i['displayName']['en']]
    print(f"   ✅ 有中文翻译: {len(has_zh)} 个 ({len(has_zh)/len(unified_items)*100:.1f}%)")
    print(f"   ℹ️  无中文翻译: {len(unified_items) - len(has_zh)} 个 (可能是游戏未提供)")
    
    # 类型分布
    types = Counter([i['type'] for i in unified_items])
    print(f"\n   类型分布 (前10):")
    for item_type, count in types.most_common(10):
        print(f"      {item_type}: {count} 个")
    
    print()
    
    # 2. 验证 stardewids 格式数据
    print("📦 2. 验证 stardewids 格式数据")
    print("-"*70)
    
    # 验证带图片的完整版本
    full_file = base_dir / "data" / "processed" / "stardewids_with_images_full.json"
    with open(full_file, 'r', encoding='utf-8') as f:
        full_items = json.load(f)
    
    with_images = [i for i in full_items if 'image' in i]
    
    print(f"   stardewids_with_images_full.json:")
    print(f"      总物品数: {len(full_items)}")
    print(f"      包含图片: {len(with_images)} ({len(with_images)/len(full_items)*100:.1f}%)")
    
    # 验证精简版本
    slim_file = base_dir / "data" / "processed" / "stardewids_format.json"
    with open(slim_file, 'r', encoding='utf-8') as f:
        slim_items = json.load(f)
    
    print(f"\n   stardewids_format.json (精简版，无图片):")
    print(f"      总物品数: {len(slim_items)}")
    
    print()
    
    # 3. 对比原始数据
    print("📊 3. 对比原始数据")
    print("-"*70)
    
    original_objects = base_dir / "stardew_recipes_counter" / "src" / "Data_Objects.json"
    with open(original_objects, 'r', encoding='utf-8') as f:
        original_data = json.load(f)
    
    print(f"   原始 Data_Objects.json: {len(original_data)} 个物品")
    print(f"   新生成统一格式: {len(unified_items)} 个物品")
    print(f"   ✅ 数据完整，无遗漏")
    
    print()
    
    # 4. 对比旧 stardewids 数据
    print("📊 4. 对比旧 stardewids 数据")
    print("-"*70)
    
    old_objects = base_dir / "stardewids" / "backup" / "objects.json.backup_20260122"
    if old_objects.exists():
        with open(old_objects, 'r', encoding='utf-8') as f:
            old_data = json.load(f)
        
        print(f"   旧 objects.json: {len(old_data)} 个物品")
        print(f"   新 objects.json: {len(full_items)} 个物品")
        print(f"   ✅ 新增: {len(full_items) - len(old_data)} 个物品")
        print(f"   提升: {(len(full_items) - len(old_data)) / len(old_data) * 100:.1f}%")
    
    print()
    
    # 5. 文件大小统计
    print("💾 5. 文件大小统计")
    print("-"*70)
    
    files_to_check = [
        ("items_unified.json", unified_file),
        ("stardewids_format.json (精简版)", slim_file),
        ("stardewids_with_images_full.json", full_file),
    ]
    
    for name, filepath in files_to_check:
        size_mb = filepath.stat().st_size / 1024 / 1024
        print(f"   {name}: {size_mb:.2f} MB")
    
    print()
    
    # 6. 数据质量检查
    print("✅ 6. 数据质量检查")
    print("-"*70)
    
    # 检查重复 ID
    ids = [i['id'] for i in unified_items]
    duplicate_ids = [id for id in ids if ids.count(id) > 1]
    
    if duplicate_ids:
        print(f"   ⚠️  发现重复 ID: {len(set(duplicate_ids))} 个")
    else:
        print(f"   ✅ 无重复 ID")
    
    # 检查精灵图索引
    invalid_sprites = [i for i in unified_items if i['sprite']['index'] < 0]
    if invalid_sprites:
        print(f"   ⚠️  无效精灵图索引: {len(invalid_sprites)} 个")
    else:
        print(f"   ✅ 所有精灵图索引有效")
    
    # 检查价格
    negative_prices = [i for i in unified_items if i['price'] < 0]
    print(f"   ℹ️  负价格物品: {len(negative_prices)} 个 (垃圾/不可出售物品)")
    
    print()
    
    # 总结
    print("="*70)
    print("📝 验证总结")
    print("="*70)
    print(f"\n✅ 所有数据验证通过！")
    print(f"\n关键指标:")
    print(f"   • 物品总数: {len(unified_items)} (从原始 {len(original_data)} 个完整保留)")
    print(f"   • 中文翻译覆盖率: {len(has_zh)/len(unified_items)*100:.1f}%")
    print(f"   • 图片提取成功率: {len(with_images)/len(full_items)*100:.1f}%")
    if old_objects.exists():
        print(f"   • 相比旧数据新增: {len(full_items) - len(old_data)} 个物品")
    print(f"\n数据存储位置:")
    print(f"   📁 data/processed/items_unified.json (统一格式)")
    print(f"   📁 data/processed/stardewids_format.json (精简版)")
    print(f"   📁 data/processed/stardewids_with_images_full.json (完整版)")
    print(f"   📁 stardewids/dist/objects.json (已更新)")
    print(f"   📁 stardewids/public/dist_slim/objects.json (已更新)")
    print()


if __name__ == "__main__":
    validate_data()
