"""修复异常宽度的贴图文件"""
import os
from PIL import Image

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
assets_dir = os.path.join(BASE_DIR, "assets")
problem_file = "Mods_FlashShifter.StardewValleyExpandedCP_Birch Water.png"
problem_path = os.path.join(assets_dir, problem_file)

print(f"🔧 修复异常贴图: {problem_file}")

# 检查文件
with Image.open(problem_path) as img:
    w, h = img.size
    print(f"   原始尺寸: {w}x{h}")
    
    # 创建 16x16 的新图像，使用透明背景
    new_img = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    
    # 将原图粘贴到左上角（保持原样）
    new_img.paste(img, (0, 0))
    
    # 保存修复后的图像
    new_img.save(problem_path)
    print(f"   ✓ 已修复为: 16x16 (添加 1px 透明边距)")

print(f"\n✨ 修复完成! 请重新运行 build_db.py")
