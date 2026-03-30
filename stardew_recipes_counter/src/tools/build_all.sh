#!/bin/bash
# 一键构建脚本

set -e  # 遇到错误立即退出

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="$BASE_DIR/venv"

cd "$BASE_DIR"

echo "============================================================"
echo "🚀 星露谷食谱项目一键构建"
echo "============================================================"

# 检查虚拟环境
if [ ! -d "$VENV_DIR" ]; then
    echo "❌ 虚拟环境不存在，正在创建..."
    python3 -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"
    pip install Pillow
else
    source "$VENV_DIR/bin/activate"
fi

echo ""
echo "📋 步骤 1/3: 扫描贴图资源..."
python "$BASE_DIR/tools/list_textures.py" > "$BASE_DIR/export_commands.txt"
echo "✓ 已生成贴图导出命令: export_commands.txt"

echo ""
echo "🔧 步骤 2/3: 检查并修复异常贴图..."
if [ -f "$BASE_DIR/tools/fix_abnormal_texture.py" ]; then
    python "$BASE_DIR/tools/fix_abnormal_texture.py" 2>/dev/null || echo "✓ 无需修复"
fi

echo ""
echo "🔨 步骤 3/3: 构建最终数据库..."
python "$BASE_DIR/tools/build_db.py"

echo ""
echo "🧪 运行项目诊断..."
python "$BASE_DIR/tools/diagnose.py"

echo ""
echo "============================================================"
echo "✨ 构建完成！"
echo "============================================================"
echo ""
echo "📂 生成的文件:"
echo "   - final_recipes.json ($(wc -l < "$BASE_DIR/final_recipes.json") 行)"
echo "   - export_commands.txt ($(wc -l < "$BASE_DIR/export_commands.txt") 行)"
echo ""
echo "🌐 启动本地服务器:"
echo "   python -m http.server 8888"
echo ""
echo "🔗 访问地址:"
echo "   http://localhost:8888/enhanced_index.html"
echo ""
