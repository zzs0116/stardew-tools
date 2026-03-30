# 🚀 星露谷食谱项目 - 快速入门指南

## 📦 5 分钟快速部署

### 步骤 1: 激活环境并构建
```bash
cd src
./tools/build_all.sh
```

### 步骤 2: 启动服务
```bash
python -m http.server 8888
```

### 步骤 3: 打开浏览器
访问：http://localhost:8888/enhanced_index.html

---

## 🔧 常见问题解决

### Q1: 运行 tools/build_db.py 报错 "No module named 'PIL'"
```bash
cd src
source venv/bin/activate
pip install Pillow
```

### Q2: 图标显示不正确/显示成整张贴图
**原因：** 异常宽度的贴图文件

**解决：**
```bash
python tools/fix_abnormal_texture.py
python tools/build_db.py
```

### Q3: 某些食谱显示为 "Unknown(123)"
**原因：** 缺少翻译数据

**解决：**
1. 在游戏中执行：`patch export Strings/Objects`
2. 将 `Strings_Objects.json` 放到 `src/` 目录
3. 重新运行 `tools/build_db.py`

### Q4: 找不到某个 Mod 的食谱
**原因：** 贴图资源未导出

**解决：**
1. 运行 `python tools/list_textures.py > export_commands.txt`
2. 在 SMAPI 控制台执行导出命令
3. 将 PNG 文件放到 `src/assets/` 目录
4. 重新运行 `tools/build_db.py`

---

## 🎯 核心文件说明

| 文件 | 用途 | 何时使用 |
|------|------|----------|
| `tools/build_db.py` | 构建最终数据库 | 每次修改数据后 |
| `tools/diagnose.py` | 检查项目健康度 | 排查问题时 |
| `tools/list_textures.py` | 扫描贴图路径 | 添加新 Mod 后 |
| `tools/fix_abnormal_texture.py` | 修复异常贴图 | 图标显示异常时 |
| `tools/build_all.sh` | 一键构建 | 初次部署或重建 |

---

## 📊 数据更新流程

```
游戏更新/安装新 Mod
    ↓
导出游戏数据 (patch export)
    ↓
扫描贴图路径 (tools/list_textures.py)
    ↓
导出贴图资源 (SMAPI 控制台)
    ↓
构建数据库 (tools/build_db.py)
    ↓
运行诊断 (tools/diagnose.py)
    ↓
刷新浏览器查看结果
```

---

## 🎨 自定义样式

修改 `enhanced_index.html` 中的 CSS：

```css
/* 修改主题色 */
.header {
    background: linear-gradient(to right, #YOUR_COLOR_1, #YOUR_COLOR_2);
}

/* 修改卡片样式 */
.card {
    border-radius: 12px;  /* 圆角 */
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);  /* 阴影 */
}
```

---

## 🐛 调试技巧

### 检查数据是否正确
```bash
jq '.[] | select(.name == "煎鸡蛋")' final_recipes.json
```

### 查看所有未翻译项
```bash
jq '.[] | select(.name | contains("Unknown"))' final_recipes.json
```

### 统计 Mod 食谱数量
```bash
jq '[.[] | .texture] | group_by(.) | map({texture: .[0], count: length})' final_recipes.json
```

### 找出最复杂的配方
```bash
jq 'sort_by(.ingredients | length) | reverse | .[0:5] | .[] | {name, ing_count: (.ingredients | length)}' final_recipes.json
```

---

## ⚡ 性能优化

### 1. 压缩 JSON
```bash
jq -c . final_recipes.json > final_recipes.min.json
```

### 2. 启用 gzip 压缩
```python
# 使用支持压缩的服务器
python -m http.server 8888 --bind 0.0.0.0
```

### 3. 懒加载图片
在 `enhanced_index.html` 中添加：
```html
<img loading="lazy" ...>
```

---

## 📱 移动端适配

项目已支持响应式设计，在移动设备上自动调整布局。

---

## 🔗 有用的链接

- [Stardew Valley Wiki](https://stardewvalleywiki.com/)
- [SMAPI 文档](https://smapi.io/)
- [Pillow 文档](https://pillow.readthedocs.io/)

---

**最后更新：2026-01-19**
