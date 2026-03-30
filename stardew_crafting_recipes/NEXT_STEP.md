# BigCraftables 翻译文件补充说明

## 当前状态

✅ **已完成**：
- BigCraftables 数据文件已加载（332 个物品）
- 脚本能正确识别和处理 BigCraftable 类型的配方

⚠️ **需要补充**：
- BigCraftables 的中文翻译文件

## 抓取翻译文件

在 SMAPI 控制台运行：
```bash
patch export "Strings/BigCraftables" "~/Documents/Projects/stardew_tools/stardew_crafting_recipes/data/"
```

这会在 `data/` 目录生成 `Strings_BigCraftables.json` 文件。

## 文件内容示例

生成的文件应该包含像这样的翻译：
```json
{
  "Chest_Name": "箱子",
  "Chest_Description": "可以用来储存物品。",
  "Furnace_Name": "熔炉",
  "Furnace_Description": "可以将矿石冶炼成锭。",
  ...
}
```

## 下一步

抓取完成后，我会：
1. 更新数据处理脚本，加载 BigCraftables 翻译
2. 重新运行脚本生成完整的中文数据
3. 验证修复效果（箱子、熔炉等应该显示正确的中文名）
