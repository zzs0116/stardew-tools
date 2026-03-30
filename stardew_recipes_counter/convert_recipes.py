import json
import csv
import io
import os

csv_content = """RSV Mod Cooking Recipes,Ingredients,Recipe Source
Apricot Juice,Apricot,Pastry Shop
Arugula Roll,"Mountain Arugula(3), Hot Pepper(2)",Pika's Restaurant
Autumnal Serenity,"Fixer Eel, Northern Limequat, Highland Jostaberry, Lava Lily",Pika's Restaurant
Autumn Dew Drop Juice,"Autumn Drop Berry, Wild Plum, Blackberry",Pika's Restaurant
Clementine Cake,"Wheat Flour, Sugar, Orange, Ridgeside Clementine(2)",Shanice - 8 Hearts
Clementine Juice,Ridgeside Clementine,Pastry Shop
Cherry Berry Shakey,"Ridge Cherry, Cherry",Pika's Restaurant
Crunchy Bagel,"Wheat Flour, Egg",Paula - 8 Hearts
Fluffy Apple Crumble,"Wheat Flour, Hazelnut(3), Apple, Ridge Wild Apple",Blair - 8 Hearts
Forage Souffle,"Egg, Snow Yam, Ridge Cherry, Ridgeside Clementine, Autumn Drop Berry",Lorenzo - 8 Hearts
Forest Halva,Sugar(5),Louie - 8 Hearts
Fried Fish a la Ridge,"Oil, Ridgeside Bass, Ridgeside Clementine, Mountain Arugula, Highland Chard",Pika's Restaurant
Fried Mountain Greens,"Oil, Highland Chard(2), Mountain Arugula",Pika's Restaurant
Ginger Arugula Fried Rice,"Mountain Arugula, Rice, Ginger",Pika's Restaurant
Ginger Rangpur Meringue,"Paradise Rangpur, Sugar, Ginger",Pastry Shop
Highland Blueberry Pie,"Wheat Flour, Sugar, Blueberry, Frost Clump Berry",Malaya - 8 Hearts
Highland Ice Cream,"Large Milk, Mountain Chico",Pika's Restaurant
Highland Revani,"Wheat Flour, Egg, Highland Jostaberry",Sonny - 8 Hearts
Holiday Ice,"Mango, Milk, Paradise Rangpur",Sean - 8 Hearts
Hundred Flavor Doughnut,"Wheat Flour, Strawberry, Blueberry, Green Bean, Spiritual Essence(5), Ancient Fruit(5)",Pastry Shop
Honey Ginger Whitefish,"Mountain Whitefish, Honey, Ginger",Pika's Restaurant
Honey Glazed Salad,"Honey, Red Cabbage, Highland Chard, Ridge Cherry",Pika's Restaurant
Jumpy Coffee Cake,"Wheat Flour, Sugar, Coffee Bean, Mountain Chico",Kiarra - 8 Hearts
Kedi Delight,"Sugar, Goat Milk, Honey, Desert Tangelo, Ember Blood Lime",Pastry Shop
Keks Style Shortcake,"Wheat Flour, Strawberry, Egg, Cherry Pluot",Pastry Shop
Kek's Small Dream,"Wheat Flour, Strawberry, Ridge Cherry",Pastry Shop
Matcha Latte,"Coffee, Green Tea",Pastry Shop
Mistbloom Syrup,Mountain Mistbloom(5),Lola - 8 Hearts
Pillowsoft Cheezy Sandwich,"Wheat Flour, Goat Cheese, Cheese, Mountain Arugula",Pastry Shop
Pink Frosted Sprinkled Doughnut,"Wheat Flour, Sugar, Strawberry, Highland Jostaberry",Pastry Shop
Pumpkin Darling Slice,"Wheat Flour, Sugar, Pumpkin, Mountain Arugula, Mountain Plumcot",Kimpoi - 8 Hearts
Ridge Apple Cake,"Wheat Flour, Egg, Apple, Ridge Wild Apple",Carmen - 8 Hearts
Ridge Fruity Plate,"Autumn Drop Berry, Ridge Wild Apple, Frost Clump Berry, Highland Chard",Pika's Restaurant
Ridge Mosaic Cake,"Wheat Flour, Sugar, Egg",Burnt - 8 Hearts
Ridgeside Shaketini,"Ridge Wild Apple, Ridgeside Clementine, Peach",Pika's Restaurant
Snow Bowl Surprise,"Ridge Cherry, Frost Clump Berry(2), Honey",Pika's Restaurant
Snowball Slurpee,"Ridgeside Clementine, Frost Clump Berry, Crystal Fruit",Pika's Restaurant
Springtime Primetime,"Crimson Spiked Clam, Cherry Pluot, Mountain Plumcot, Mountain Arugula",Pika's Restaurant
Strawberry Lover Pie,"Wheat Flour, Sugar, Strawberry, Ridge Wild Apple",Irene - 8 Hearts
Summer Mountain Blessing,"Bladetail Sturgeon, Paradise Rangpur, Tropi Ugli Fruit, Mountain Chico",Pika's Restaurant
Summit Iced Tea,"Sugar, Mountain Plumcot",Pika's Restaurant
Sweet Cranberry Cheesecake,"Wheat Flour, Sugar, Cheese, Cranberries(2), Northern Limequat",Faye - 8 Hearts
Tropic Mango Cake,"Wheat Flour, Egg, Mango, Tropi Ugli Fruit",Maive - 8 Hearts
Wild Apple Juice,Ridge Wild Apple(2),Pastry Shop
Winter Night Feast,"Cardia Septal Jellyfish, Mountain Whitefish, Sierra Wintergreen, Frost Clump Berry",Pika's Restaurant
Zesty Tuna,"Tuna, Ridgeside Clementine, Mountain Chico, Autumn Drop Berry",Pika's Restaurant"""

zh_mapping = {
    "apricot-juice": "杏子汁",
    "arugula-roll": "芝麻菜卷",
    "aurorean-iris": "极光鸢尾花",
    "autumn-dew-drop-juice": "秋露汁",
    "autumn-drop-berry": "秋落莓",
    "autumnal-serenity": "秋收静悦",
    "bladetail-sturgeon": "刀尾鲟鱼",
    "caped-tree-frog": "斗篷树蛙",
    "cardia-septal-jellyfish": "贲门隔水母",
    "cherry-berry-shakey": "樱桃浆果奶昔",
    "cherry-pluot": "樱桃杏李",
    "clementine-cake": "无籽红橘蛋糕",
    "clementine-juice": "无籽红橘果汁",
    "crimson-spiked-clam": "绯红刺蛤",
    "crunchy-bagel": "酥脆贝果",
    "cutthroat-trout": "割喉鳟鱼",
    "deep-ridge-angler": "深山鮟鱇鱼",
    "desert-tangelo": "沙漠橘柚",
    "elven-comb": "精灵梳子",
    "ember-blood-lime": "灰烬血莱姆",
    "entombed-ring": "被掩埋的戒指",
    "everfrost-stone": "永霜石",
    "fairytale-lionfish": "童话狮子鱼",
    "fixer-eel": "疗愈鳗鱼",
    "fluffy-apple-crumble": "蓬松苹果酥",
    "forage-souffle": "野果蛋奶酥",
    "forest-amancay": "森林六出花",
    "forest-halva": "森林酥糖",
    "foxbloom": "狐灵花",
    "freddies-sword": "弗雷迪的剑",
    "fried-fish-a-la-ridge": "山脊炸酥鱼",
    "fried-mountain-greens": "高山炸时蔬",
    "frost-clump-berry": "霜丛浆果",
    "ginger-arugula-fried-rice": "仔姜芝麻菜炒饭",
    "ginger-rangpur-meringue": "姜黎檬蛋白酥皮",
    "glove-of-the-assassin": "刺客手套",
    "golden-rose-fin": "金玫瑰鳍鱼",
    "golden-skull-coral": "金颅珊瑚",
    "harvester-trout": "收割鳟鱼",
    "highland-blueberry-pie": "高地蓝莓派",
    "highland-butterwort": "高地捕虫堇",
    "highland-chard": "高地甜菜",
    "highland-ice-cream": "高地冰淇淋",
    "highland-jostaberry": "高地醋栗樱桃",
    "highland-revani": "高地小蛋糕",
    "holiday-ice": "度假冰淇淋",
    "hollowed-bear": "空心泰迪熊",
    "honey-ginger-whitefish": "蜂蜜姜白鱼",
    "honey-glazed-salad": "蜜汁色拉",
    "hundred-flavor-doughnut": "百味甜甜圈",
    "inked-fossil": "墨迹化石",
    "jumpy-coffee-cake": "脉动咖啡蛋糕",
    "kedi-delight": "凯蒂乐",
    "keks-small-dream": "凯克的小梦想",
    "keks-style-shortcake": "凯克式司康蛋糕",
    "lava-lily": "熔岩百合",
    "lovers-sorrow": "情人之殇",
    "lullaby-carp": "摇篮曲鲤鱼",
    "matcha-latte": "抹茶拿铁",
    "mistbloom-syrup": "迷雾花糖浆",
    "moose-statue": "伟大河神雕像",
    "mountain-arugula": "高山芝麻菜",
    "mountain-chico": "高山人心果",
    "mountain-hokkaido": "高山北海道花",
    "mountain-mistbloom": "高山迷雾花",
    "mountain-plumcot": "高山李杏",
    "mountain-redbelly-dace": "高山红腹鲮",
    "mountain-whitefish": "高山白鱼",
    "nightblack-diamond": "夜黑钻石",
    "northern-limequat": "北方莱姆金柑",
    "old-lucky-foxtail-charm": "老旧的幸运狐尾护符",
    "opal-halo": "猫眼石光轮",
    "pale-candelabrum": "苍白烛台",
    "paradise-rangpur": "天堂黎檬",
    "pebble-back-crab": "石背蟹",
    "pillowsoft-cheezy-sandwich": "超软奶酪三明治",
    "pink-frosted-sprinkled-doughnut": "粉红糖霜甜甜圈",
    "pumpkin-darling-slice": "南瓜达令切片蛋糕",
    "relic-fox-mask": "古代狐狸面具",
    "richards-glasses": "理查德的眼镜",
    "ridge-apple-cake": "山脊苹果蛋糕",
    "ridge-azorean-flower": "山脊勿忘我",
    "ridge-bluegill": "山脊蓝鳃鱼",
    "ridge-cherry": "山脊樱桃",
    "ridge-fruity-plate": "山脊水果拼盘",
    "ridge-mosaic-cake": "山脊马赛克蛋糕",
    "ridge-wild-apple": "山脊野苹果",
    "ridgeside-bass": "山脊鲈鱼",
    "ridgeside-clementine": "山脊无籽红橘",
    "ridgeside-monkshood": "山脊乌头",
    "ridgeside-shaketini": "山脊奶昔酒",
    "sapphire-pearl": "蓝宝石珍珠",
    "shell-bracelet": "贝壳手镯",
    "sierra-wintergreen": "山岭冬青",
    "silver-fish-bones": "银鱼骨",
    "skulpin-fish": "小褐鳕",
    "snow-bowl-surprise": "惊喜雪碗",
    "snowball-slurpee": "雪球思乐冰",
    "sockeye-salmon": "红鲑",
    "spiritual-essence": "灵魂精华",
    "springtime-primetime": "初春金时",
    "strawberry-lover-pie": "草莓情人派",
    "summer-mountain-blessing": "盛夏礼赞",
    "summit-iced-tea": "天山冰茶",
    "summit-snowbell": "天山雪铃",
    "sweet-cranberry-cheesecake": "香甜蔓越莓芝士蛋糕",
    "tropi-ugli-fruit": "热带丑橘",
    "tropic-mango-cake": "热带芒果蛋糕",
    "village-hero-sculpture": "乡村英雄雕塑",
    "violet-devils-claw": "紫罗兰魔爪",
    "warp-totem-ridgeside": "里奇赛德村传送图腾",
    "waterfall-snakehead": "瀑布黑鱼",
    "wild-apple-juice": "野苹果汁",
    "winter-night-feast": "冬夜盛宴",
    "yellow-wood-sculpture": "黄色木雕",
    "yuumas-ring": "佑马的戒指",
    "zesty-tuna": "滋滋美味金枪鱼"
}

output = {}
f = io.StringIO(csv_content)
reader = csv.reader(f)
next(reader) # skip header

for row in reader:
    if not row: continue
    english_name = row[0]
    # Transform: spaces to hyphens OR underscores, lowercase
    key_hyphen = english_name.lower().replace(" ", "-")
    key_underscore = english_name.lower().replace(" ", "_")
    
    if key_hyphen in zh_mapping:
        output[english_name] = zh_mapping[key_hyphen]
    elif key_underscore in zh_mapping:
        output[english_name] = zh_mapping[key_underscore]

target_dir = "/Users/edisonzhang/Documents/Projects/stardew_tools/stardew_recipes_counter/data/zh"
if not os.path.exists(target_dir):
    os.makedirs(target_dir)

target_path = os.path.join(target_dir, "Recipes (RSV).json")
with open(target_path, 'w', encoding='utf-8') as outfile:
    json.dump(output, outfile, ensure_ascii=False, indent=4)

print(f"Successfully wrote {len(output)} translations to {target_path}")
