#!/usr/bin/env python3
"""
配方图片提取脚本

从 src/craftables_png 中读取已导出的源图，为 crafting_data.json 中的配方产物生成缩略图。
如主目录中未找到，则回退到 src/png。

当前仍需要额外导出的源图（按数据中的 Texture 路径推导）：
- Textures/DN.SnS/BlessedTools
- TileSheets\\Objects_2
- Textures/DN.SnS/SnSMachines
- Textures/DN.SnS/TeleportCircle
- Mods\\MNF.MoreNewFish\\Objects\\Objects
- Mods\\Objects\\MNF.MoreNewFish_fish_hatchery
- Mods\\Lumisteria.MtVapius\\Machines
- Mods\\Lumisteria.MtVapius\\Objects
- Cornucopia.ArtisanMachines/Craftables
- Mods/leclair.bcmagicbench/Texture
- Mods/DTZ.DowntownZuzuCP/Items/Qi Crystal
- Mods/EnD/Objects
- Mods\\FlashShifter.StardewValleyExpandedCP\\Marsh Tonic
"""

import json
import shutil
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image


BASE_DIR = Path(__file__).resolve().parent
CRAFTING_DATA_PATH = BASE_DIR / "data" / "crafting_data.json"
OBJECTS_DATA_PATH = BASE_DIR / "data" / "Data_Objects.json"
BIG_CRAFTABLES_DATA_PATH = BASE_DIR / "data" / "Data_BigCraftables.json"
WEAPONS_DATA_PATH = BASE_DIR / "data" / "Data_Weapons.json"

PRIMARY_SOURCE_DIR = BASE_DIR / "src" / "craftables_png"
FALLBACK_SOURCE_DIR = BASE_DIR / "src" / "png"
OUTPUT_OBJECTS_DIR = BASE_DIR / "images" / "objects"
OUTPUT_CRAFTABLES_DIR = BASE_DIR / "images" / "craftables"

SCALE_FACTOR = 3


def normalize_texture_key(value):
    if not value:
        return ""
    return value.replace("\\", "/").strip().lower()


TEXTURE_SOURCE_SPECS = {
    "maps/springobjects": {
        "file": "Maps_springobjects.png",
        "tile_width": 16,
        "tile_height": 16,
    },
    "tilesheets/craftables": {
        "file": "TileSheets_Craftables.png",
        "tile_width": 16,
        "tile_height": 32,
    },
    "tilesheets/objects_2": {
        "file": "TileSheets_Objects_2.png",
        "tile_width": 16,
        "tile_height": 16,
    },
    "textures/dn.sns/snsobjects": {
        "file": "Textures_DN.SnS_SnSObjects.png",
        "tile_width": 16,
        "tile_height": 16,
    },
    "textures/dn.sns/snsmachines": {
        "file": "Textures_DN.SnS_SnSMachines.png",
        "tile_width": 16,
        "tile_height": 32,
    },
    "textures/dn.sns/snsarsenal": {
        "file": "Textures_DN.SnS_SnSArsenal.png",
        "tile_width": 16,
        "tile_height": 16,
    },
    "mods/lemurkat.eastscarp/esobjects": {
        "file": "Mods_Lemurkat.EastScarp_esobjects.png",
        "tile_width": 16,
        "tile_height": 16,
    },
    "mods/rafseazz.rsvcp/objects/objects": {
        "file": "Mods_Rafseazz.RSVCP_Objects_Objects.png",
        "tile_width": 16,
        "tile_height": 16,
    },
    "mods/skellady.sbvcp/genericobjects": {
        "file": "Mods_skellady.SBVCP_GenericObjects.png",
        "tile_width": 16,
        "tile_height": 16,
    },
    "mods/skellady.sbvcp/miscitems": {
        "file": "Mods_skellady.SBVCP_MiscItems.png",
        "tile_width": 16,
        "tile_height": 16,
    },
    "mods/skellady.sbvcp/machines": {
        "file": "Mods_skellady.SBVCP_Machines.png",
        "tile_width": 16,
        "tile_height": 32,
    },
    "mods/maddogbearfam/nonweaponequipment": {
        "file": "Mods_MadDogBearFam_NonWeaponEquipment.png",
        "tile_width": 16,
        "tile_height": 16,
    },
    "mods/mnf.morenewfish/objects/objects": {
        "file": "Mods_MNF.MoreNewFish_Objects_Objects.png",
        "tile_width": 16,
        "tile_height": 16,
    },
    "mods/objects/mnf.morenewfish_fish_hatchery": {
        "file": "Mods_Objects_MNF.MoreNewFish_fish_hatchery.png",
        "tile_width": 16,
        "tile_height": 32,
    },
    "mods/lumisteria.mtvapius/machines": {
        "file": "Mods_Lumisteria.MtVapius_Machines.png",
        "tile_width": 16,
        "tile_height": 32,
    },
    "mods/lumisteria.mtvapius/objects": {
        "file": "Mods_Lumisteria.MtVapius_Objects.png",
        "tile_width": 16,
        "tile_height": 16,
    },
    "cornucopia.artisanmachines/craftables": {
        "file": "Cornucopia.ArtisanMachines_Craftables.png",
        "fallback_files": ["Cornucopia.ArtisanMachines_Objects.png"],
        "tile_width": 16,
        "tile_height": 32,
    },
    "mods/leclair.bcmagicbench/texture": {
        "file": "Mods_leclair.bcmagicbench_Texture.png",
        "tile_width": 16,
        "tile_height": 32,
    },
    "mods/dtz.downtownzuzucp/items/qi crystal": {
        "file": "Mods_DTZ.DowntownZuzuCP_Items_Qi Crystal.png",
        "tile_width": 16,
        "tile_height": 16,
    },
    "mods/end/objects": {
        "file": "Mods_EnD_Objects.png",
        "tile_width": 16,
        "tile_height": 16,
    },
    "textures/dn.sns/teleportcircle": {
        "file": "Textures_DN.SnS_TeleportCircle.png",
        "tile_width": 16,
        "tile_height": 16,
    },
    "textures/dn.sns/blessedtools": {
        "file": "Textures_DN.SnS_BlessedTools.png",
        "tile_width": 16,
        "tile_height": 16,
    },
}

DIRECT_IMAGE_OVERRIDES = {
    "FlashShifter.StardewValleyExpandedCP_Armor_Elixir": "Mods_FlashShifter.StardewValleyExpandedCP_Armor Elixir.png",
    "FlashShifter.StardewValleyExpandedCP_Bombardier_Elixir": "Mods_FlashShifter.StardewValleyExpandedCP_Bombardier Elixir.png",
    "FlashShifter.StardewValleyExpandedCP_Haste_Elixir": "Mods_FlashShifter.StardewValleyExpandedCP_Haste Elixir.png",
    "FlashShifter.StardewValleyExpandedCP_Hedge_Fence_Tilesheet": "Mods_FlashShifter.StardewValleyExpandedCP_Hedge Fence.png",
    "FlashShifter.StardewValleyExpandedCP_Hero_Elixir": "Mods_FlashShifter.StardewValleyExpandedCP_Hero Elixir.png",
    "FlashShifter.StardewValleyExpandedCP_Seed_Cookie": "Mods_FlashShifter.StardewValleyExpandedCP_Seed Cookie.png",
    "FlashShifter.StardewValleyExpandedCP_Small_Hardwood_Fence_Tilesheet": "Mods_FlashShifter.StardewValleyExpandedCP_Small Hardwood Fence.png",
    "FlashShifter.StardewValleyExpandedCP_Sun_Totem": "Mods_FlashShifter.StardewValleyExpandedCP_Sun Totem.png",
    "FlashShifter.StardewValleyExpandedCP_Wind_Totem": "Mods_FlashShifter.StardewValleyExpandedCP_Wind Totem.png",
    "FlashShifter.StardewValleyExpandedCP_Yarn_Spooler": "Mods_FlashShifter.StardewValleyExpandedCP_Yarn Spooler.png",
    "FlashShifter.StardewValleyExpandedCP_Marsh_Tonic": "Mods_FlashShifter.StardewValleyExpandedCP_Marsh Tonic.png",
}


def load_json(path):
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def ensure_output_dirs():
    OUTPUT_OBJECTS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_CRAFTABLES_DIR.mkdir(parents=True, exist_ok=True)


def find_source_path(filename, fallback_files=None):
    candidates = [filename]
    if fallback_files:
        candidates.extend(fallback_files)

    for candidate in candidates:
        primary = PRIMARY_SOURCE_DIR / candidate
        if primary.exists():
            return primary
        fallback = FALLBACK_SOURCE_DIR / candidate
        if fallback.exists():
            return fallback
    return None


def scale_image(image, tile_width, tile_height):
    if SCALE_FACTOR <= 1:
        return image
    new_size = (tile_width * SCALE_FACTOR, tile_height * SCALE_FACTOR)
    return image.resize(new_size, Image.NEAREST)


def crop_from_grid(sheet, sprite_index, tile_width, tile_height):
    columns = sheet.width // tile_width
    if columns <= 0:
        raise ValueError("invalid columns")

    row = sprite_index // columns
    col = sprite_index % columns
    x = col * tile_width
    y = row * tile_height
    if x + tile_width > sheet.width or y + tile_height > sheet.height:
        raise ValueError(
            f"sprite index {sprite_index} out of bounds for sheet {sheet.width}x{sheet.height} "
            f"with tile {tile_width}x{tile_height}"
        )
    return sheet.crop((x, y, x + tile_width, y + tile_height))


def get_item_data(item_id, is_big_craftable, objects_data, big_craftables_data, weapons_data):
    if is_big_craftable and item_id in big_craftables_data:
        return big_craftables_data[item_id]
    if item_id in objects_data:
        return objects_data[item_id]
    if item_id in weapons_data:
        return weapons_data[item_id]
    if item_id in big_craftables_data:
        return big_craftables_data[item_id]
    return None


def resolve_output_path(recipe):
    rel = recipe.get("图片链接", "").lstrip("./")
    if not rel:
        return None
    return BASE_DIR / rel


def can_use_existing_target(target_path):
    return target_path is not None and target_path.exists()


def main():
    print("📖 加载数据...")
    recipes = load_json(CRAFTING_DATA_PATH)
    objects_data = load_json(OBJECTS_DATA_PATH)
    big_craftables_data = load_json(BIG_CRAFTABLES_DATA_PATH)
    weapons_data = load_json(WEAPONS_DATA_PATH)

    ensure_output_dirs()

    source_cache = {}
    processed = 0
    generated = 0
    copied_direct = 0
    preserved_existing = 0

    missing_by_source = Counter()
    missing_by_reason = Counter()
    missing_examples = defaultdict(list)

    for recipe in recipes:
        processed += 1
        output = recipe.get("产物", {})
        item_id = output.get("id")
        is_big_craftable = bool(output.get("是大型可制作物"))
        target_path = resolve_output_path(recipe)

        if not item_id or target_path is None:
            continue

        target_path.parent.mkdir(parents=True, exist_ok=True)

        override_file = DIRECT_IMAGE_OVERRIDES.get(item_id)
        if override_file:
            source_path = find_source_path(override_file)
            if source_path:
                shutil.copy2(source_path, target_path)
                generated += 1
                copied_direct += 1
                continue
            if can_use_existing_target(target_path):
                preserved_existing += 1
                continue
            missing_by_source[recipe.get("来源", "未知")] += 1
            missing_by_reason["缺少单图源文件"] += 1
            if len(missing_examples["缺少单图源文件"]) < 8:
                missing_examples["缺少单图源文件"].append((recipe.get("名称_EN", ""), item_id, override_file))
            continue

        item_data = get_item_data(item_id, is_big_craftable, objects_data, big_craftables_data, weapons_data)
        texture = item_data.get("Texture") if item_data else None
        sprite_index = item_data.get("SpriteIndex") if item_data else None

        if texture:
            texture_key = normalize_texture_key(texture)
            source_spec = TEXTURE_SOURCE_SPECS.get(texture_key)
            reason_missing_label = f"缺少源图: {texture}"
        elif is_big_craftable:
            texture_key = "tilesheets/craftables"
            source_spec = TEXTURE_SOURCE_SPECS[texture_key]
            reason_missing_label = "缺少源图: TileSheets/Craftables"
        else:
            texture_key = "maps/springobjects"
            source_spec = TEXTURE_SOURCE_SPECS[texture_key]
            reason_missing_label = "缺少源图: Maps/springobjects"

        if sprite_index is None:
            try:
                sprite_index = int(item_id)
            except (TypeError, ValueError):
                if can_use_existing_target(target_path):
                    preserved_existing += 1
                    continue
                missing_by_source[recipe.get("来源", "未知")] += 1
                missing_by_reason["缺少 SpriteIndex"] += 1
                if len(missing_examples["缺少 SpriteIndex"]) < 8:
                    missing_examples["缺少 SpriteIndex"].append((recipe.get("名称_EN", ""), item_id, texture or ""))
                continue

        if not source_spec:
            if can_use_existing_target(target_path):
                preserved_existing += 1
                continue
            missing_by_source[recipe.get("来源", "未知")] += 1
            missing_by_reason["未配置纹理映射"] += 1
            if len(missing_examples["未配置纹理映射"]) < 8:
                missing_examples["未配置纹理映射"].append((recipe.get("名称_EN", ""), item_id, texture or ""))
            continue

        source_path = find_source_path(
            source_spec["file"],
            source_spec.get("fallback_files"),
        )
        if not source_path:
            if can_use_existing_target(target_path):
                preserved_existing += 1
                continue
            missing_by_source[recipe.get("来源", "未知")] += 1
            missing_by_reason[reason_missing_label] += 1
            if len(missing_examples[reason_missing_label]) < 8:
                missing_examples[reason_missing_label].append((recipe.get("名称_EN", ""), item_id, source_spec["file"]))
            continue

        cache_key = source_spec["file"]
        sheet = source_cache.get(cache_key)
        if sheet is None:
            sheet = Image.open(source_path).convert("RGBA")
            source_cache[cache_key] = sheet

        try:
            tile_width = source_spec["tile_width"]
            tile_height = source_spec["tile_height"]
            cropped = crop_from_grid(sheet, int(sprite_index), tile_width, tile_height)
            scaled = scale_image(cropped, tile_width, tile_height)
            scaled.save(target_path)
            generated += 1
        except Exception as exc:
            if can_use_existing_target(target_path):
                preserved_existing += 1
                continue
            missing_by_source[recipe.get("来源", "未知")] += 1
            missing_by_reason["裁切失败"] += 1
            if len(missing_examples["裁切失败"]) < 8:
                missing_examples["裁切失败"].append((recipe.get("名称_EN", ""), item_id, str(exc)))

    remaining_missing = []
    for recipe in recipes:
        target_path = resolve_output_path(recipe)
        if target_path is None or not target_path.exists():
            remaining_missing.append(recipe)

    print("\n✅ 提取完成！")
    print(f"   配方总数: {processed}")
    print(f"   生成/覆盖: {generated}")
    print(f"   其中单图直拷贝: {copied_direct}")
    print(f"   保留已有文件: {preserved_existing}")
    print(f"   剩余缺图: {len(remaining_missing)}")

    print("\nMISSING_BY_SOURCE")
    if remaining_missing:
        grouped = Counter(recipe.get("来源", "未知") for recipe in remaining_missing)
        for source, count in grouped.most_common():
            print(f"   {source}: {count}")
    else:
        print("   无")

    print("\nMISSING_BY_REASON")
    if missing_by_reason:
        for reason, count in missing_by_reason.most_common():
            print(f"   {reason}: {count}")
    else:
        print("   无")

    if missing_examples:
        print("\nMISSING_EXAMPLES")
        for reason, entries in missing_examples.items():
            print(f"   [{reason}]")
            for name_en, item_id, detail in entries:
                print(f"      - {name_en} | {item_id} | {detail}")


if __name__ == "__main__":
    main()
