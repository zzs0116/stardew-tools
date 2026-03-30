#!/usr/bin/env python3
"""
Stardew Valley 物品数据整合脚本
合并 Data_Objects.json 和 Strings_Objects.json，生成统一的物品数据
"""

import json
import re
import base64
from pathlib import Path
from typing import Dict, Any, Optional, List
from PIL import Image
import io


class StardewDataMerger:
    """星露谷物品数据合并器"""
    
    # 默认纹理配置
    DEFAULT_TEXTURE = "Maps/springobjects"
    SPRITE_SIZE = 16
    SHEET_WIDTH = 24  # springobjects.png 宽度为 24 个精灵（384px / 16px）
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.recipes_dir = base_dir / "stardew_recipes_counter" / "src"
        self.stardewids_dir = base_dir / "stardewids"
        self.output_dir = base_dir / "data" / "processed"
        self.sprites_dir = base_dir / "stardew_recipes_counter" / "src" / "assets"
        
        # 加载数据
        self.data_objects = {}
        self.strings_objects = {}
        self.sprite_cache = {}  # 缓存已提取的精灵图
        
    def load_json(self, filepath: Path) -> Dict:
        """加载 JSON 文件"""
        print(f"📖 加载文件: {filepath.name}")
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_json(self, data: Any, filepath: Path, indent: int = 2):
        """保存 JSON 文件"""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
        print(f"✅ 保存文件: {filepath.name} ({len(data)} 项)")
    
    def parse_localized_text(self, text: str) -> Optional[str]:
        """
        解析本地化文本引用
        例如: "[LocalizedText Strings\\Objects:WildHorseradish_Name]" -> "WildHorseradish_Name"
        """
        if not text or not isinstance(text, str):
            return None
        
        # 尝试匹配本地化文本引用（兼容单反斜杠和双反斜杠）
        match = re.match(r'\[LocalizedText Strings\\+Objects:([^\]]+)\]', text)
        if match:
            return match.group(1)
        return text
    
    def get_chinese_text(self, key: str, fallback: str = "") -> str:
        """获取中文翻译"""
        return self.strings_objects.get(key, fallback)
    
    def calculate_sprite_position(self, sprite_index: int, texture: str = None) -> Dict:
        """
        计算精灵图在纹理中的位置
        
        Args:
            sprite_index: 精灵索引
            texture: 纹理文件路径（用于确定布局）
        
        Returns:
            包含 x, y, width, height 的字典
        """
        # springobjects 的布局是 24 列
        if texture is None or "springobjects" in (texture or ""):
            cols = self.SHEET_WIDTH
        else:
            # 其他纹理可能有不同的列数，这里默认 24
            cols = self.SHEET_WIDTH
        
        x = (sprite_index % cols) * self.SPRITE_SIZE
        y = (sprite_index // cols) * self.SPRITE_SIZE
        
        return {
            "x": x,
            "y": y,
            "width": self.SPRITE_SIZE,
            "height": self.SPRITE_SIZE
        }
    
    def extract_sprite_as_base64(self, sprite_index: int, texture_name: str = "Maps_springobjects") -> Optional[str]:
        """
        从纹理图中提取单个精灵并转换为 base64
        
        Args:
            sprite_index: 精灵索引
            texture_name: 纹理文件名
        
        Returns:
            base64 编码的 PNG 图片
        """
        # 缓存键
        cache_key = f"{texture_name}_{sprite_index}"
        if cache_key in self.sprite_cache:
            return self.sprite_cache[cache_key]
        
        # 查找纹理文件
        texture_file = self.sprites_dir / f"{texture_name}.png"
        if not texture_file.exists():
            print(f"⚠️  纹理文件不存在: {texture_file}")
            return None
        
        try:
            # 打开纹理图
            img = Image.open(texture_file)
            
            # 计算位置
            pos = self.calculate_sprite_position(sprite_index)
            
            # 裁剪精灵
            sprite = img.crop((
                pos['x'],
                pos['y'],
                pos['x'] + pos['width'],
                pos['y'] + pos['height']
            ))
            
            # 转换为 base64
            buffer = io.BytesIO()
            sprite.save(buffer, format='PNG')
            b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            # 缓存
            self.sprite_cache[cache_key] = f"data:image/png;base64,{b64}"
            
            return self.sprite_cache[cache_key]
            
        except Exception as e:
            print(f"⚠️  提取精灵失败 {sprite_index}: {e}")
            return None
    
    def merge_item_data(self, item_id: str, item_data: Dict) -> Dict:
        """
        合并单个物品的数据
        
        Args:
            item_id: 物品 ID
            item_data: Data_Objects.json 中的物品数据
        
        Returns:
            合并后的物品数据
        """
        raw_display_name = item_data.get('DisplayName', '')
        raw_description = item_data.get('Description', '')
        
        # 检查是否已经是中文（直接包含中文字符）
        def has_chinese(text):
            import re
            return bool(re.search(r'[\u4e00-\u9fff]', text or ''))
        
        # 处理 DisplayName
        if has_chinese(raw_display_name):
            # 直接是中文，使用它
            display_name_cn = raw_display_name
        else:
            # 尝试解析 [LocalizedText] 引用
            name_key = self.parse_localized_text(raw_display_name)
            display_name_cn = self.get_chinese_text(name_key, item_data.get('Name', ''))
        
        # 处理 Description
        if has_chinese(raw_description):
            # 直接是中文，使用它
            description_cn = raw_description
        else:
            # 尝试解析 [LocalizedText] 引用
            desc_key = self.parse_localized_text(raw_description)
            description_cn = self.get_chinese_text(desc_key, '')
        
        # 纹理信息
        texture = item_data.get('Texture') or self.DEFAULT_TEXTURE
        sprite_index = item_data.get('SpriteIndex', 0)
        sprite_pos = self.calculate_sprite_position(sprite_index, texture)
        
        # 构建统一数据结构
        merged = {
            "id": item_id,
            "name": item_data.get('Name', ''),
            "displayName": {
                "en": item_data.get('Name', ''),
                "zh": display_name_cn
            },
            "description": {
                "en": item_data.get('Description', ''),
                "zh": description_cn
            },
            "type": item_data.get('Type', ''),
            "category": item_data.get('Category', 0),
            "price": item_data.get('Price', 0),
            "sprite": {
                "texture": texture.replace('\\', '/'),
                "index": sprite_index,
                "x": sprite_pos['x'],
                "y": sprite_pos['y'],
                "width": sprite_pos['width'],
                "height": sprite_pos['height']
            }
        }
        
        # 可选字段
        if item_data.get('Edibility') is not None and item_data['Edibility'] != -300:
            merged['edibility'] = item_data['Edibility']
        
        if item_data.get('IsDrink'):
            merged['isDrink'] = True
        
        if item_data.get('ContextTags'):
            merged['contextTags'] = item_data['ContextTags']
        
        return merged
    
    def convert_to_stardewids_format(self, item: Dict, with_image: bool = False) -> Dict:
        """
        转换为 stardewids 格式
        
        Args:
            item: 统一格式的物品数据
            with_image: 是否包含 base64 图片
        
        Returns:
            stardewids 格式的数据
        """
        result = {
            "id": item['id'],
            "objectType": item['type'],
            "names": {
                "data-en-US": item['displayName']['en'],
                "data-zh-CN": item['displayName']['zh']
            }
        }
        
        # 添加 base64 图片（如果需要）
        if with_image:
            texture_name = item['sprite']['texture'].replace('Maps/', 'Maps_')
            image_b64 = self.extract_sprite_as_base64(
                item['sprite']['index'],
                texture_name
            )
            if image_b64:
                result['image'] = image_b64
        
        return result
    
    def run(self):
        """执行数据合并流程"""
        print("\n" + "="*60)
        print("🌾 Stardew Valley 数据整合工具")
        print("="*60 + "\n")
        
        # 1. 加载原始数据
        print("📦 步骤 1: 加载原始数据")
        print("-" * 60)
        self.data_objects = self.load_json(
            self.recipes_dir / "Data_Objects.json"
        )
        self.strings_objects = self.load_json(
            self.recipes_dir / "Strings_Objects.json"
        )
        
        print(f"   Data_Objects: {len(self.data_objects)} 个物品")
        print(f"   Strings_Objects: {len(self.strings_objects)} 个翻译\n")
        
        # 2. 合并数据
        print("🔧 步骤 2: 合并数据")
        print("-" * 60)
        merged_items = []
        
        for item_id, item_data in self.data_objects.items():
            try:
                merged = self.merge_item_data(item_id, item_data)
                merged_items.append(merged)
            except Exception as e:
                print(f"⚠️  处理物品 {item_id} 时出错: {e}")
        
        print(f"   成功合并: {len(merged_items)} 个物品\n")
        
        # 3. 按类型分类
        print("📂 步骤 3: 按类型分类")
        print("-" * 60)
        items_by_type = {}
        for item in merged_items:
            item_type = item['type']
            if item_type not in items_by_type:
                items_by_type[item_type] = []
            items_by_type[item_type].append(item)
        
        for item_type, items in sorted(items_by_type.items()):
            print(f"   {item_type}: {len(items)} 个")
        print()
        
        # 4. 保存统一格式数据
        print("💾 步骤 4: 保存统一格式数据")
        print("-" * 60)
        
        # 保存完整数据
        self.save_json(
            merged_items,
            self.output_dir / "items_unified.json",
            indent=2
        )
        
        # 保存按类型分类的数据
        for item_type, items in items_by_type.items():
            safe_type = item_type.replace(' ', '_').replace('/', '_')
            self.save_json(
                items,
                self.output_dir / "by_type" / f"{safe_type}.json",
                indent=2
            )
        
        print()
        
        # 5. 生成 stardewids 格式（不含图片）
        print("🔄 步骤 5: 生成 stardewids 格式（精简版）")
        print("-" * 60)
        
        stardewids_items = [
            self.convert_to_stardewids_format(item, with_image=False)
            for item in merged_items
        ]
        
        self.save_json(
            stardewids_items,
            self.output_dir / "stardewids_format.json",
            indent=1  # 更紧凑
        )
        
        print()
        
        # 6. 生成带图片的版本（采样 50 个用于测试）
        print("🖼️  步骤 6: 生成带图片的样本数据")
        print("-" * 60)
        
        # 只为前 50 个物品生成图片（测试用）
        sample_items = merged_items[:50]
        stardewids_with_images = []
        
        for i, item in enumerate(sample_items, 1):
            print(f"   处理 {i}/{len(sample_items)}: {item['displayName']['zh']}", end='\r')
            stardewids_item = self.convert_to_stardewids_format(item, with_image=True)
            stardewids_with_images.append(stardewids_item)
        
        print()
        self.save_json(
            stardewids_with_images,
            self.output_dir / "stardewids_with_images_sample.json",
            indent=1
        )
        
        print()
        
        # 7. 生成统计报告
        print("📊 步骤 7: 生成统计报告")
        print("-" * 60)
        
        stats = {
            "total_items": len(merged_items),
            "by_type": {
                item_type: len(items)
                for item_type, items in items_by_type.items()
            },
            "categories": {},
            "edible_items": len([i for i in merged_items if 'edibility' in i]),
            "drinks": len([i for i in merged_items if i.get('isDrink')]),
        }
        
        # 按 category 统计
        for item in merged_items:
            cat = item['category']
            stats['categories'][cat] = stats['categories'].get(cat, 0) + 1
        
        self.save_json(
            stats,
            self.output_dir / "statistics.json",
            indent=2
        )
        
        print(f"   总物品数: {stats['total_items']}")
        print(f"   可食用: {stats['edible_items']}")
        print(f"   饮品: {stats['drinks']}")
        print()
        
        # 完成
        print("="*60)
        print("✨ 数据整合完成！")
        print("="*60)
        print(f"\n📁 输出目录: {self.output_dir}")
        print(f"   - items_unified.json (完整数据)")
        print(f"   - stardewids_format.json (stardewids 格式，不含图片)")
        print(f"   - stardewids_with_images_sample.json (样本数据，含图片)")
        print(f"   - by_type/*.json (按类型分类)")
        print(f"   - statistics.json (统计报告)")
        print()


def main():
    """主函数"""
    # 项目根目录
    base_dir = Path("/Users/edisonzhang/Documents/Projects/stardew_tools")
    
    # 创建合并器并运行
    merger = StardewDataMerger(base_dir)
    merger.run()


if __name__ == "__main__":
    main()
