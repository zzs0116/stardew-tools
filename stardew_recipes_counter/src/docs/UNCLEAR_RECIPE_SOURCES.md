# 不明确来源清单

最后更新：2026-03-05

## 记录规则

- 只记录“当前数据中无法确定明确获取方式”的食谱。
- 如果后续查明来源，保留历史并标注“已确认”。

## 当前不明确项

### 1) 岩浆鳗鱼烩葫芦

- 名称：岩浆鳗鱼烩葫芦
- 内部ID：`DN.SnS_lavaeelandstirfriedancientbottlegourd`
- 现状：
  - `Data_CookingRecipes` 来源字段为 `false`
  - `Data_mail` / `Data_SpecialOrders` / `Data_Shops` 未找到明确“食谱获取”记录
- 备注：先按 `other` 处理

### 2) 波尔特火龙饮

- 名称：波尔特火龙饮
- 内部ID：`DN.SnS_portfiredrakesparkler`
- 现状：
  - `Data_CookingRecipes` 来源字段为 `false`
  - `Data_Shops` 仅确认成品在 `DN.SnS_LMCafe` 随机售卖（`IsRecipe: false`）
  - `Data_mail` 未找到对应食谱邮件
  - 存在 `Core.Cirrus.Generic.LateHeart.22` 对话线索，但该键更像高好感日常对话，不是明确事件解锁键
- 备注：先按 `other` 处理

### 3) 费什肯蜜桃馅饼

- 名称：费什肯蜜桃馅饼
- 内部ID：`MadDog.HashtagBearFam_FerskenPeachCobbler`
- 现状：
  - `Data_CookingRecipes` 来源字段为 `null`
  - `Data_mail` 存在 `bearfam.ferskenpeachcobbler`，但附送的是成品 `item id`，不是 `cookingRecipe`
  - `Data_Shops` / `Data_SpecialOrders` 未找到明确食谱获取记录
- 备注：先按 `other` 处理

### 4) 香辣披萨

- 名称：香辣披萨
- 内部ID：`Bagi.Nora_SpicyPizza`
- 现状：
  - `Data_CookingRecipes` 该条配方字段格式异常，缺少可解析来源段
  - `Data_mail` / `Data_Shops` / `Data_SpecialOrders` 未找到明确食谱获取记录
- 备注：先按 `other` 处理

### 5) 腌黄瓜玉米热狗

- 名称：腌黄瓜玉米热狗
- 内部ID：`Bagi.Nora_PickledCornDog`
- 现状：
  - `Data_CookingRecipes` 同组条目格式异常（与 `Bagi.Nora_SpicyPizza` 同类），来源不明确
  - `Data_mail` / `Data_Shops` / `Data_SpecialOrders` 未找到明确食谱获取记录
- 备注：先按 `other` 处理

### 6) 切片桃子

- 名称：切片桃子
- 内部ID：`MadDog.HashtagBearFam_SlicedPeaches`
- 现状：
  - `Data_CookingRecipes` 来源字段为 `null`
  - `Data_mail` 存在 `bearfam.slicedpeaches`，但附送的是成品 `item id`，不是 `cookingRecipe`
  - `Data_Shops` / `Data_SpecialOrders` 未找到明确食谱获取记录
- 备注：先按 `other` 处理
