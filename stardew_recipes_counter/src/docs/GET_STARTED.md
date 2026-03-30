# 🚀 开始使用指南

## ⚡ 30 秒快速启动

```bash
cd src
./tools/open_browser.sh
```

就这么简单！浏览器会自动打开食谱百科界面。

---

## 📋 验证清单

在开始使用前，确认以下内容：

- [x] ✅ 所有 Python 脚本已创建
- [x] ✅ 所有 Web 界面已创建
- [x] ✅ 所有文档已完善
- [x] ✅ 数据已成功构建（final_recipes.json）
- [x] ✅ 26 项测试全部通过
- [x] ✅ 所有贴图资源已规范化

---

## 🎯 推荐工作流程

### 第一次使用

1. **启动服务并浏览**
   ```bash
   cd src
   ./tools/open_browser.sh
   ```

2. **查看完成报告**
   - 访问：http://localhost:8888/completion_infographic.html
   - 了解项目的所有功能和成就

3. **尝试搜索与统计**
   - 在增强版界面搜索"煎蛋"
   - 展开统计面板查看食材总数
   - 查看不同 Mod 的食谱

### 日常使用

```bash
cd src
python -m http.server 8888
# 访问 http://localhost:8888/enhanced_index.html
```

### 游戏更新后

```bash
# 1. 在游戏中导出新数据
patch export Data/Objects
patch export Data/CookingRecipes
patch export Strings/Objects

# 2. 重新构建
cd src
./tools/build_all.sh
```

---

## 🔗 重要链接（本地访问）

| 页面 | 地址 | 说明 |
|------|------|------|
| 🌟 **增强版界面** | http://localhost:8888/enhanced_index.html | 推荐！完整功能 |
| 🎉 完成报告 | http://localhost:8888/completion_infographic.html | 项目成就 |
| 🏗️ 架构图 | http://localhost:8888/visualize_architecture.html | 技术架构 |
| 🧪 测试页 | http://localhost:8888/test_page.html | 图标测试 |

---

## 💡 使用技巧

### 1. 快速查找食谱
- **按食谱名称**: 输入"煎蛋"
- **按原料**: 输入"牛奶"
- **按分类**: 点击🥚🥛🐟标签

### 2. 查看详细信息
- 每个卡片显示完整的原料清单和数量
- 图标都是像素级精确渲染

### 3. 导出数据
```bash
# 导出为 Markdown 表格
cd src
python tools/export_to_markdown.py > my_recipes.md
```

### 4. 检查项目健康度
```bash
cd src
python tools/diagnose.py          # 快速检查
python tools/validate_project.py  # 完整验证
python tools/project_summary.py   # 详细报告
```

---

## 🛠️ 常见问题

### Q: 如何停止服务器？
A: 在终端按 `Ctrl + C`

### Q: 如何更改端口？
A: 修改命令为 `python -m http.server 8000`（改为其他端口）

### Q: 如何分享给朋友？
A: 
1. 压缩整个 `src/` 文件夹
2. 发送给朋友
3. 告诉他们运行 `./tools/open_browser.sh`

### Q: 如何添加新 Mod？
A: 
1. 在游戏中安装 Mod
2. 重新执行 patch export
3. 运行 `./tools/build_all.sh`

---

## 📊 项目文件说明

### 🌟 必看文件

1. **FINAL_SUMMARY.md** - 完整项目总结
2. **README.md** - 详细技术文档
3. **quick_start.md** - 快速入门指南

### 🔧 常用脚本

- `tools/build_db.py` - 重新构建数据库
- `tools/diagnose.py` - 诊断项目健康
- `tools/validate_project.py` - 运行所有测试

### 🌐 Web 界面

- `enhanced_index.html` ⭐ 推荐使用
- `completion_infographic.html` - 成就报告

---

## 🎉 恭喜！

你的项目已经完全就绪，现在可以：

1. ✅ **立即使用** - 启动服务器开始浏览
2. ✅ **分享给朋友** - 帮助其他玩家
3. ✅ **自定义扩展** - 添加新功能
4. ✅ **游戏更新** - 随时重新构建

---

**享受你的星露谷食谱百科吧！** 🍲✨

Made with ❤️ for Stardew Valley
