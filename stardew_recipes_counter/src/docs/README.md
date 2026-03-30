# 🍲 星露谷食谱百科 (Stardew Valley Recipe Counter)

一个本地化的网页工具，用于查询星露谷物语 1.6 版本（及所有已安装 Mod）中的烹饪配方、原料清单和像素风格图标展示。

## ✨ 项目特性

- **完整 Mod 支持**：自动抓取并解析所有已安装 Mod 的食谱数据（SVE、RSV、Downtown Zuzu 等）
- **中文本地化**：完美解决 1.6 版本的 `[LocalizedText]` 令牌问题
- **像素级图标**：277+ 张贴图资源，动态计算坐标，支持各种非标准尺寸
- **智能分类**：自动识别并展示"任意鸡蛋"、"任意牛奶"等分类原料
- **搜索 + 统计**：实时搜索食谱和原料，并统计食材总数
- **响应式设计**：适配不同屏幕尺寸

## 📊 当前数据

- **303 个食谱**（包含原版 + Mod）
- **62 个贴图资源包**
- **100% 翻译覆盖率**（无 Unknown 项）

## 🚀 快速开始

### 1. 数据准备

从 SMAPI 导出游戏数据：
```bash
# 在 Stardew Valley 中按 ~ 键打开控制台
patch export Data/Objects
patch export Data/CookingRecipes
patch export Strings/Objects
```

将导出的 JSON 文件放到 `src/` 目录。

### 2. 导出贴图资源

使用 `tools/list_textures.py` 扫描所有引用的贴图路径：
```bash
cd src
python tools/list_textures.py > export_commands.txt
```

在 SMAPI 控制台中执行导出命令，并将 PNG 文件放到 `src/assets/` 目录。

### 3. 构建数据库

```bash
cd src
source venv/bin/activate  # 激活虚拟环境
python tools/build_db.py
```

这将生成 `final_recipes.json`，包含预处理的坐标、翻译等数据。

### 4. 启动本地服务器

```bash
cd src
python -m http.server 8888
```

在浏览器中访问：
- 主界面：http://localhost:8888/enhanced_index.html
- 测试页：http://localhost:8888/test_page.html

## 🛠️ 项目结构

```
stardew_recipes_counter/
├── src/
│   ├── tools/
│   │   ├── build_db.py              # 数据构建脚本（核心）
│   │   ├── list_textures.py         # 贴图路径扫描器
│   │   ├── scan_translations.py     # 翻译数据扫描器
│   │   ├── diagnose.py              # 项目诊断工具
│   │   ├── fix_abnormal_texture.py  # 异常贴图修复工具
│   │   ├── build_all.sh             # 一键构建脚本
│   │   └── open_browser.sh          # 本地预览启动器
│   ├── docs/
│   │   ├── README.md
│   │   ├── GET_STARTED.md
│   │   ├── QUICK_REFERENCE.txt
│   │   ├── PROJECT_OVERVIEW.txt
│   │   ├── FINAL_SUMMARY.md
│   │   ├── CHANGELOG.md
│   │   ├── recipes_list.md
│   │   └── quick_start.md
│   ├── Data_Objects.json        # 物品数据（SMAPI 导出）
│   ├── Data_CookingRecipes.json # 食谱数据（SMAPI 导出）
│   ├── Strings_Objects.json     # 本地化数据（SMAPI 导出）
│   ├── final_recipes.json       # 预处理后的最终数据
│   ├── enhanced_index.html      # 增强版前端（推荐）
│   ├── test_page.html           # 图标测试页
│   ├── visualize_architecture.html # 架构图
│   ├── completion_infographic.html # 完成度看板
│   ├── assets/                  # 贴图资源（277+ PNG）
│   └── venv/                    # Python 虚拟环境
│
├── data/                        # 其他数据文件
└── convert_recipes.py           # 外部数据转化脚本
```

## 🔧 核心技术

### 数据层
- **SMAPI patch export**：抓取合并后的游戏数据（包含 Mod）
- **正则表达式**：解析 1.6 版本的 `[LocalizedText Strings/Objects:123]` 令牌
- **分类 ID 映射**：将 `-5` 等负数 ID 映射到具体图标

### 资源层
- **Pillow (PIL)**：动态检测贴图宽度，计算每张图的列数
- **坐标计算**：`x = (index % cols) * 16`, `y = (index // cols) * 16`
- **异常处理**：修复非 16 倍数宽度的贴图（如 15px → 16px）

### 展示层
- **CSS Sprite**：通过 `margin-left` 和 `margin-top` 负值定位图标
- **image-rendering: pixelated**：保持像素风格
- **max-width: none !important**：防止浏览器自动缩放

## 🐛 已解决的坑点

### 1. "杂草诅咒" (Index 0 问题)
- **现象**：大部分物品显示为杂草
- **原因**：1.6 版本部分物品缺少 `ParentSheetIndex`
- **解决**：优先使用 `SpriteIndex`，并增加智能回退逻辑

### 2. "全家福"缩略图 (CSS 压缩问题)
- **现象**：图标格子里塞进整张巨大贴图
- **原因**：浏览器的 `img { max-width: 100% }` 默认样式
- **解决**：强制 `max-width: none !important`

### 3. "两半"或"货不对板" (坐标偏移问题)
- **现象**：图标显示错位或显示相邻物品
- **原因**：Mod 贴图列数不统一（1 列、8 列、24 列等）
- **解决**：用 Pillow 动态读取宽度，计算真实列数

### 4. 除以零错误
- **现象**：`ZeroDivisionError` 在处理小图片时崩溃
- **原因**：部分 Mod 贴图宽度 < 16px（如 15px）
- **解决**：`cols = max(1, w // 16)` 确保列数至少为 1

## 📈 项目诊断

运行诊断工具检查项目健康度：
```bash
cd src
python tools/diagnose.py
```

输出示例：
```
============================================================
🔍 星露谷食谱项目诊断报告
============================================================

📊 数据统计:
   ✓ 食谱总数: 303

🖼️  贴图资源检查:
   ✓ 所有贴图宽度均为 16 的倍数

🌐 翻译完整性:
   ✓ 所有食谱名称已翻译
   ✓ 所有原料名称已翻译

📐 坐标计算检查:
   ✓ 所有坐标计算正常

🏷️  分类图标统计:
   分类原料使用频率:
      - 任意鸡蛋: 47 次
      - 任意牛奶: 47 次
      - 任意鱼类: 4 次

✨ 诊断完成!
============================================================
```

## 🎨 前端功能

### 搜索功能
- 实时搜索食谱名称和原料
- 支持模糊匹配

### 食材统计
- 展开/收起统计面板
- 按总消耗量排序展示食材

### 响应式卡片
- 自适应网格布局
- 悬停动画效果
- 像素风格图标

## 📝 依赖

- Python 3.7+
- Pillow (PIL): `pip install Pillow`
- jq (可选，用于 JSON 处理)
- ImageMagick (可选，用于图片诊断)

## 🔮 未来计划

- [ ] 添加解锁条件展示
- [ ] 支持导出 PDF/PNG 图鉴
- [ ] 添加食谱来源（原版/哪个 Mod）
- [ ] 支持多语言切换
- [ ] 添加 Buff 效果展示
- [ ] 整合原料来源（商店/采集/制作）

## 📄 License

MIT License

## 🙏 致谢

- [Stardew Valley](https://www.stardewvalley.net/) by ConcernedApe
- [SMAPI](https://smapi.io/) - Mod 框架
- Mod 作者：FlashShifter (SVE), Rafseazz (RSV), MadDogBearFam, Lemurkat 等

---

**Made with ❤️ for Stardew Valley farmers**
