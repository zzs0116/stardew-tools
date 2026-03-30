#!/bin/bash
echo "🚀 正在启动星露谷食谱百科..."
echo ""

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$BASE_DIR"

python3 -m http.server 8888 > /dev/null 2>&1 &
SERVER_PID=$!
echo "✓ 服务器已启动 (PID: $SERVER_PID)"
sleep 1
open http://localhost:8888/enhanced_index.html
echo "✓ 浏览器已打开"
echo ""
echo "📝 使用说明:"
echo "  - 在搜索框输入关键词查找食谱"
echo "  - 使用统计面板查看食材总数"
echo "  - 按 Ctrl+C 停止服务器"
echo ""
echo "🔗 其他页面:"
echo "  - 测试页: http://localhost:8888/test_page.html"
echo "  - 架构图: http://localhost:8888/visualize_architecture.html"
echo ""
wait $SERVER_PID
