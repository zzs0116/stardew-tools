#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复名称和解锁条件相同的配方
将这些配方的解锁条件改为"待补充"
"""

import json

def fix_duplicate_unlock_conditions():
    # 读取数据
    with open('data/crafting_data.json', 'r', encoding='utf-8') as f:
        recipes = json.load(f)
    
    # 统计和修改
    found_count = 0
    modified_recipes = []
    
    for recipe in recipes:
        name = recipe.get('名称', '')
        unlock = recipe.get('解锁条件', '')
        
        # 检查名称和解锁条件是否相同
        if name and unlock and name == unlock:
            found_count += 1
            modified_recipes.append({
                '名称': name,
                '名称_EN': recipe.get('名称_EN', ''),
                '原解锁条件': unlock
            })
            # 修改解锁条件
            recipe['解锁条件'] = '待补充'
    
    # 保存修改后的数据
    with open('data/crafting_data.json', 'w', encoding='utf-8') as f:
        json.dump(recipes, f, ensure_ascii=False, indent=2)
    
    # 输出结果
    print(f'✅ 找到 {found_count} 个名称和解锁条件相同的配方')
    print('\n修改的配方列表：')
    for item in modified_recipes:
        print(f"  - {item['名称']} ({item['名称_EN']})")
    
    print(f'\n✅ 已将这些配方的解锁条件改为"待补充"')

if __name__ == '__main__':
    fix_duplicate_unlock_conditions()
