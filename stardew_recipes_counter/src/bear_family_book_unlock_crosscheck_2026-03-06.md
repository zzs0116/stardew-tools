# Bear Family 书本解锁交叉核对（2026-03-06）

范围：仅统计 4 本书（`TerenRecipes` / `BearRecipes` / `GunnarRecipes` / `SondraRecipes`）通过 `MarkCookingRecipeKnown` 直接解锁的 24 道食谱。

## A. 书本以外仍有其他解锁路径（8）

1. `Joja 冰淇淋苏打` (`MadDog.HashtagBearFam_JojaFloat`)
- 书本：`MadDog.HashtagBearFam_TerenRecipes`
- 其他路径：邮件 `Teren.JojaFloat`
- 备注：触发器条件为 `SEASON summer` + `PLAYER_HAS_SEEN_EVENT Current MadDog.BearFam.16199000` + `PLAYER_FRIENDSHIP_POINTS Current MadDog.HashtagBearFam.Teren 250`

2. `莫德女王布丁` (`MadDog.HashtagBearFam_DronningMaud`)
- 书本：`MadDog.HashtagBearFam_BearRecipes`
- 其他路径：邮件 `Gudrun.DronningMaud`

3. `荆棘莓果酱` (`MadDog.HashtagBearFam_StoneBrambleJam`)
- 书本：`MadDog.HashtagBearFam_BearRecipes`
- 其他路径：邮件 `Gudrun.BrambleJam`
- 备注：存在补偿触发器 `MadDog.Bearfam_Gudrun.BrambleJamFix`

4. `桑德拉的冬日奇趣棒` (`MadDog.HashtagBearFam_SondraWinterBar`)
- 书本：`MadDog.HashtagBearFam_SondraRecipes`
- 其他路径：`SEASON_DAY winter 10` + 邮件 `bearfam.winterwonderbar`

5. `桑德拉的春日酥饼` (`MadDog.HashtagBearFam_SondraSpringtimeShortbread`)
- 书本：`MadDog.HashtagBearFam_SondraRecipes`
- 其他路径：`SEASON_DAY spring 10` + 邮件 `bearfam.springtimeshortbread`

6. `桑德拉的夏日点心蛋糕` (`MadDog.HashtagBearFam_SondraSummerCake`)
- 书本：`MadDog.HashtagBearFam_SondraRecipes`
- 其他路径：`SEASON_DAY summer 10` + 邮件 `bearfam.summersnackcake`

7. `桑德拉的秋日苹果曲奇` (`MadDog.HashtagBearFam_SondraAutumnCookie`)
- 书本：`MadDog.HashtagBearFam_SondraRecipes`
- 其他路径：`SEASON_DAY fall 10` + 邮件 `bearfam.autumnapplecookie`

8. `荆棘莓派` (`MadDog.HashtagBearFam_BrambleBerryPie`)
- 书本：`MadDog.HashtagBearFam_SondraRecipes`
- 其他路径：邮件 `Gudrun.BrambleBerryPie`

## B. 目前仅检出“读书直学”路径（16）

- `三重诱惑布朗尼` (`MadDog.HashtagBearFam_TTBrownies`)
- `香蕉面包` (`MadDog.HashtagBearFam_BananaBread`)
- `玫瑰纸杯蛋糕` (`MadDog.HashtagBearFam_RoseCupcakes`)
- `玉米松糕` (`MadDog.HashtagBearFam_CornbreadMuffins`)
- `芝麻黑麦面包` (`MadDog.HashtagBearFam_SesameBrownBread`)
- `蜂蜜全麦面包` (`MadDog.HashtagBearFam_HoneyWheatBread`)
- `费什肯桃蜂蜜酒大酒杯` (`MadDog.HashtagBearFam_FerskenPeach_Mead_Tankard`)
- `费什肯蜜桃馅饼` (`MadDog.HashtagBearFam_FerskenPeachCobbler`)
- `切片桃子` (`MadDog.HashtagBearFam_SlicedPeaches`)
- `蜂蜜蓝莓蛋糕` (`MadDog.HashtagBearFam_HoneyCakes`)
- `冈纳的劣质药剂` (`MadDog.HashtagBearFam_GunnarBadPotion`)
- `冈纳的第一种药剂` (`MadDog.HashtagBearFam_GunnarFirstPotion`)
- `冈纳的神秘药剂` (`MadDog.HashtagBearFam_GunnarMysteryPotion`)
- `冈纳的第二种药剂` (`MadDog.HashtagBearFam_GunnarSecondPotion`)
- `冈纳的第三种药剂` (`MadDog.HashtagBearFam_GunnarThirdPotion`)
- `冈纳的古怪药剂` (`MadDog.HashtagBearFam_GunnarWeirdPotion`)

## C. 备注

- 桑德拉四季食谱在 `Data/CookingRecipes` 中写的是 `SEASON_DAY * 10`，但 `Data/Triggers` 邮件发送日期分别是春10、夏13、秋16、冬19，存在日期不一致，后续可单独定规范。
