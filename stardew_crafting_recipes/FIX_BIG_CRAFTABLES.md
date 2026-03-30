# 修复 Big Craftables 数据映射问题

## 问题原因

星露谷物语有两套物品 ID 系统：
1. **Objects (普通物品)**：ID 0-999+，存储在 `Data/Objects`
2. **Big Craftables (大型可制作物)**：ID 0-999+，存储在 `Data/BigCraftables`

配方中的产物 ID 可能是这两种之一，需要用不同的数据源来查询。

**示例问题：**
- Chest 配方产物 ID 是 `130`
- 这个 ID 在 Objects 中是"金枪鱼"（错误）
- 应该查询 BigCraftables 中的 ID 130（箱子）

## 解决步骤

### 1. 从游戏抓取 BigCraftables 数据

在 SMAPI 控制台中运行：
```bash
patch export "Data/BigCraftables" "~/Documents/Projects/stardew_tools/stardew_crafting_recipes/data/"
```

这会生成 `Data_BigCraftables.json` 文件。

### 2. 数据文件说明

抓取后的文件格式类似于 `Data_Objects.json`：
```json
{
  "130": {
    "Name": "Chest",
    "DisplayName": "[LocalizedText ...]",
    "Description": "[LocalizedText ...]",
    ...
  }
}
```

### 3. 修改数据处理脚本

脚本需要：
- 加载 `Data_BigCraftables.json`
- 在解析产物时，判断是 Object 还是 BigCraftable
- 从对应的数据源获取名称和描述

## 判断逻辑

从 `Data_CraftingRecipes.json` 来看：
- 产物 ID 如果是纯数字（如 `130`），通常是 BigCraftable
- 产物 ID 如果有特殊字符（如 `BigChest`），是命名的 BigCraftable
- 材料 ID 前缀 `(BC)` 表示 BigCraftable（如 `(BC)13`）

**配方第三个字段是关键**：
```
"Chest": "388 50/Home/130/true/default/"
           材料    类型  产物 是否Big (true=BigCraftable)
```

第四个字段 `true` 表示这是一个 BigCraftable！

## 下一步

请先运行上面的 SMAPI 命令抓取数据，然后我会更新脚本。
