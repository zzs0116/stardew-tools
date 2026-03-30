# 📝 更新日志 (Changelog)

## [1.0.0] - 2026-01-19

### ✨ 新增功能
- **完整的 Mod 支持**：支持 SVE, RSV, Downtown Zuzu 等主流 Mod
- **智能坐标计算**：动态检测贴图宽度，自适应计算图标位置
- **中文本地化**：完美解析 1.6 版本的 `[LocalizedText]` 令牌
- **分类图标映射**：智能识别"任意鸡蛋"、"任意牛奶"等分类原料
- **实时搜索**：支持食谱名称和原料的实时搜索
- **食材统计**：新增食材总数统计面板（可展开查看）
- **响应式设计**：完美适配桌面和移动设备

### 🔧 核心修复
- **修复除以零错误**：处理宽度 < 16px 的异常贴图（如 15px）
- **修复坐标偏移**：支持非标准列数的 Mod 贴图（1-24 列）
- **修复"杂草诅咒"**：优先使用 SpriteIndex，智能回退逻辑
- **修复 CSS 压缩**：强制 `max-width: none !important`
- **修复翻译缺失**：完整的 Strings/Objects 映射

### 📦 数据统计
- 303 个食谱（106 原版 + 197 Mod）
- 245 种原料
- 250 个贴图资源文件
- 62 个独立贴图资源包
- 100% 翻译完成率

### 🛠️ 开发工具
- `tools/build_db.py` - 核心构建脚本
- `tools/diagnose.py` - 项目诊断工具
- `tools/fix_abnormal_texture.py` - 贴图修复工具
- `tools/list_textures.py` - 资源扫描器
- `tools/build_all.sh` - 一键构建脚本
- `tools/project_summary.py` - 项目总结报告

### 📚 文档
- `docs/README.md` - 完整项目文档
- `docs/quick_start.md` - 快速入门指南
- `docs/CHANGELOG.md` - 本文件
- `visualize_architecture.html` - 架构可视化

### 🌐 Web 界面
- `enhanced_index.html` - 增强版界面（搜索+统计）
- `test_page.html` - 图标测试页

### 🎯 Mod 支持列表
- ✅ Vanilla (原版)
- ✅ Stardew Valley Expanded (SVE)
- ✅ Ridgeside Village (RSV)
- ✅ Downtown Zuzu
- ✅ East Scarp
- ✅ Mt. Vapius
- ✅ More Crops (Cornucopia)
- ✅ More Flowers (Cornucopia)
- ✅ Food Adjacent
- ✅ 其他 10+ Mod

### 🐛 已知问题
- 无

### 🔮 未来计划
- [ ] 添加解锁条件展示
- [ ] 支持导出 PDF/PNG 图鉴
- [ ] 添加食谱来源标记（原版/具体 Mod 名）
- [ ] 支持多语言切换（英文/中文/其他）
- [ ] 添加 Buff 效果展示
- [ ] 整合原料来源信息（商店/采集/制作）
- [ ] 添加收藏/标记功能
- [ ] 支持离线 PWA 应用

---

**版本说明：**
- 主版本号：重大功能更新或架构变更
- 次版本号：新功能添加
- 修订号：Bug 修复和小改进
