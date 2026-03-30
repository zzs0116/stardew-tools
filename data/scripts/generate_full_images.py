#!/usr/bin/env python3
"""
为全部物品生成带图片的 stardewids 格式数据
"""

import json
import base64
from pathlib import Path
from PIL import Image
import io
from tqdm import tqdm


def calculate_sprite_position(sprite_index: int, cols: int = 24, size: int = 16):
    """计算精灵图位置"""
    x = (sprite_index % cols) * size
    y = (sprite_index // cols) * size
    return {"x": x, "y": y, "width": size, "height": size}


def extract_sprite_as_base64(sprite_index: int, texture_file: Path, cols: int = 24):
    """从纹理图中提取精灵并转换为 base64"""
    if not texture_file.exists():
        return None
    
    try:
        img = Image.open(texture_file)
        pos = calculate_sprite_position(sprite_index, cols)
        
        sprite = img.crop((
            pos['x'], pos['y'],
            pos['x'] + pos['width'],
            pos['y'] + pos['height']
        ))
        
        buffer = io.BytesIO()
        sprite.save(buffer, format='PNG')
        b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return f"data:image/png;base64,{b64}"
    except Exception as e:
        return None


def main():
    base_dir = Path("/Users/edisonzhang/Documents/Projects/stardew_tools")
    input_file = base_dir / "data" / "processed" / "items_unified.json"
    output_file = base_dir / "data" / "processed" / "stardewids_with_images_full.json"
    sprites_dir = base_dir / "stardew_recipes_counter" / "src" / "assets"
    
    print("📦 加载物品数据...")
    with open(input_file, 'r', encoding='utf-8') as f:
        items = json.load(f)
    
    print(f"   找到 {len(items)} 个物品\n")
    
    print("🖼️  提取精灵图并生成数据...")
    results = []
    
    # 使用 tqdm 显示进度条
    for item in tqdm(items, desc="处理物品", unit="个"):
        # 构建结果
        result = {
            "id": item['id'],
            "objectType": item['type'],
            "names": {
                "data-en-US": item['displayName']['en'],
                "data-zh-CN": item['displayName']['zh']
            }
        }
        
        # 提取图片
        texture_name = item['sprite']['texture'].replace('Maps/', 'Maps_')
        texture_file = sprites_dir / f"{texture_name}.png"
        
        image_b64 = extract_sprite_as_base64(
            item['sprite']['index'],
            texture_file
        )
        
        if image_b64:
            result['image'] = image_b64
        
        results.append(result)
    
    print(f"\n💾 保存到 {output_file.name}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=1)
    
    # 统计
    with_images = len([r for r in results if 'image' in r])
    print(f"\n✅ 完成！")
    print(f"   总物品数: {len(results)}")
    print(f"   包含图片: {with_images}")
    print(f"   无图片: {len(results) - with_images}")
    
    # 计算文件大小
    file_size = output_file.stat().st_size / 1024 / 1024
    print(f"   文件大小: {file_size:.2f} MB")


if __name__ == "__main__":
    main()
