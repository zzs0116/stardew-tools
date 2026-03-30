"""完整的项目验证脚本"""
import json
import os
from PIL import Image

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def p(*parts):
    return os.path.join(BASE_DIR, *parts)

class ProjectValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.passed = []
        
    def test(self, name, condition, error_msg="", warning=False):
        """执行单个测试"""
        if condition:
            self.passed.append(name)
            print(f"  ✓ {name}")
        else:
            if warning:
                self.warnings.append((name, error_msg))
                print(f"  ⚠️  {name}: {error_msg}")
            else:
                self.errors.append((name, error_msg))
                print(f"  ✗ {name}: {error_msg}")
    
    def run_all_tests(self):
        print("\n" + "="*70)
        print("🧪 星露谷食谱项目 - 完整验证测试")
        print("="*70 + "\n")
        
        # 测试 1: 文件存在性检查
        print("📁 测试 1: 核心文件存在性")
        self.test("Data_Objects.json", os.path.exists(p('Data_Objects.json')))
        self.test("Data_CookingRecipes.json", os.path.exists(p('Data_CookingRecipes.json')))
        self.test("Strings_Objects.json", os.path.exists(p('Strings_Objects.json')))
        self.test("final_recipes.json", os.path.exists(p('final_recipes.json')))
        self.test("enhanced_index.html", os.path.exists(p('enhanced_index.html')))
        self.test("assets 目录", os.path.exists(p('assets')) and os.path.isdir(p('assets')))
        
        # 测试 2: 数据完整性
        print("\n📊 测试 2: 数据完整性")
        try:
            with open(p('final_recipes.json'), 'r', encoding='utf-8') as f:
                recipes = json.load(f)
            self.test("JSON 格式正确", True)
            self.test("食谱数量 > 0", len(recipes) > 0, f"只有 {len(recipes)} 个食谱")
            self.test("食谱数量合理", len(recipes) >= 100, f"食谱太少 ({len(recipes)} < 100)", warning=True)
        except Exception as e:
            self.test("JSON 解析", False, str(e))
            return
        
        # 测试 3: 数据结构验证
        print("\n🔍 测试 3: 数据结构验证")
        required_fields = ['name', 'texture', 'x', 'y', 'sw', 'ingredients']
        sample = recipes[0] if recipes else {}
        for field in required_fields:
            self.test(f"字段 '{field}' 存在", field in sample, f"缺少必需字段: {field}")
        
        # 测试 4: 翻译完整性
        print("\n🌐 测试 4: 翻译完整性")
        untranslated_recipes = [r for r in recipes if 'Unknown' in r['name'] or '[' in r['name']]
        self.test("所有食谱已翻译", len(untranslated_recipes) == 0, 
                 f"{len(untranslated_recipes)} 个食谱未翻译")
        
        untranslated_ings = sum(1 for r in recipes for ing in r['ingredients'] 
                               if 'Unknown' in ing['name'] or '[' in ing['name'])
        self.test("所有原料已翻译", untranslated_ings == 0, 
                 f"{untranslated_ings} 个原料未翻译")
        
        # 测试 5: 贴图资源验证
        print("\n🖼️  测试 5: 贴图资源验证")
        textures_used = set(item['texture'] for r in recipes for item in [r] + r['ingredients'])
        missing_textures = []
        for tex in textures_used:
            if not os.path.exists(p("assets", tex)):
                missing_textures.append(tex)
        self.test("所有贴图文件存在", len(missing_textures) == 0, 
                 f"缺少 {len(missing_textures)} 个贴图")
        
        # 测试 6: 贴图尺寸验证
        print("\n📐 测试 6: 贴图尺寸验证")
        abnormal_textures = []
        for fname in os.listdir(p('assets')):
            if fname.endswith('.png'):
                try:
                    with Image.open(p('assets', fname)) as img:
                        w, h = img.size
                        if w % 16 != 0 or h % 16 != 0:
                            abnormal_textures.append(f"{fname} ({w}x{h})")
                except:
                    pass
        self.test("所有贴图尺寸规范", len(abnormal_textures) == 0, 
                 f"{len(abnormal_textures)} 个异常尺寸", warning=True)
        
        # 测试 7: 坐标计算验证
        print("\n🧮 测试 7: 坐标计算验证")
        coord_errors = []
        for r in recipes:
            for item in [r] + r['ingredients']:
                if item['sw'] <= 0:
                    coord_errors.append(f"{item['name']}: sw={item['sw']}")
                if item['x'] < 0 or item['y'] < 0:
                    coord_errors.append(f"{item['name']}: x={item['x']}, y={item['y']}")
        self.test("所有坐标有效", len(coord_errors) == 0, 
                 f"{len(coord_errors)} 个坐标错误")
        
        # 测试 8: HTML 文件验证
        print("\n🌐 测试 8: HTML 文件验证")
        for html_file in ['enhanced_index.html', 'test_page.html']:
            if os.path.exists(p(html_file)):
                with open(p(html_file), 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.test(f"{html_file} 包含必要元素", 
                             'final_recipes.json' in content or 'assets/' in content)
        
        # 测试 9: Python 脚本验证
        print("\n🐍 测试 9: Python 脚本验证")
        scripts = ['build_db.py', 'diagnose.py', 'list_textures.py']
        for script in scripts:
            self.test(f"{script} 存在", os.path.exists(p('tools', script)))
        
        # 生成报告
        self.generate_report(recipes)
    
    def generate_report(self, recipes):
        print("\n" + "="*70)
        print("📋 验证报告")
        print("="*70)
        
        total_tests = len(self.passed) + len(self.errors) + len(self.warnings)
        print(f"\n总测试数: {total_tests}")
        print(f"  ✓ 通过: {len(self.passed)} 项")
        print(f"  ⚠️  警告: {len(self.warnings)} 项")
        print(f"  ✗ 失败: {len(self.errors)} 项")
        
        if self.warnings:
            print("\n⚠️  警告详情:")
            for name, msg in self.warnings:
                print(f"  - {name}: {msg}")
        
        if self.errors:
            print("\n✗ 错误详情:")
            for name, msg in self.errors:
                print(f"  - {name}: {msg}")
        
        print("\n" + "="*70)
        
        if len(self.errors) == 0:
            print("🎉 所有关键测试通过！项目状态: 🟢 优秀")
        elif len(self.errors) <= 2:
            print("⚠️  存在少量问题，项目状态: 🟡 良好")
        else:
            print("❌ 存在严重问题，项目状态: 🔴 需要修复")
        
        print("="*70 + "\n")
        
        # 统计信息
        print("📊 项目统计:")
        print(f"  • 食谱总数: {len(recipes)}")
        print(f"  • 原料种类: {len(set(ing['name'] for r in recipes for ing in r['ingredients']))}")
        print(f"  • 贴图资源: {len(set(item['texture'] for r in recipes for item in [r] + r['ingredients']))}")
        print(f"  • 物理文件: {len([f for f in os.listdir(p('assets')) if f.endswith('.png')])}")
        print()

if __name__ == "__main__":
    validator = ProjectValidator()
    validator.run_all_tests()
