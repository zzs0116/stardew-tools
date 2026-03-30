#!/usr/bin/env python3
"""
将金色核桃抓取结果整理成页面数据，并同步图片到金核桃子页目录。
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen


ROOT = Path("/Users/edisonzhang/Documents/Projects/stardew_tools")
SOURCE_JSON = ROOT / "data" / "processed" / "golden_walnuts_zh.json"
GUIDE_DIR = ROOT / "ginger_island_puzzle_toolbox" / "golden_walnut_guide"
IMAGES_DIR = GUIDE_DIR / "images"
OUTPUT_JS = GUIDE_DIR / "guide_data.js"
USER_AGENT = "stardew-tools-golden-walnuts-guide-builder/1.0"
TARGET_SECTIONS = ["全岛通用", "岛屿东部", "岛屿西部", "岛屿北部", "岛屿南部"]
SECTION_CODES = {
    "全岛通用": "all",
    "岛屿东部": "east",
    "岛屿西部": "west",
    "岛屿北部": "north",
    "岛屿南部": "south",
}


def normalize_section(section: str) -> str:
    if section.startswith("火山外"):
        return "岛屿北部"
    return section


def load_source() -> dict:
    with SOURCE_JSON.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def download_image(url: str, section: str, entry_index: int, image_index: int) -> str:
    parsed = urlparse(url)
    suffix = Path(parsed.path).suffix or ".png"
    section_code = SECTION_CODES.get(section, "section")
    filename = f"{section_code}-{entry_index:02d}-{image_index:02d}{suffix}"
    target = IMAGES_DIR / filename
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        request = Request(url, headers={"User-Agent": USER_AGENT})
        with urlopen(request, timeout=30) as response:
            target.write_bytes(response.read())
    return f"./images/{filename}"


def build_payload(source: dict) -> dict:
    grouped = {section: [] for section in TARGET_SECTIONS}
    counters = {section: 0 for section in TARGET_SECTIONS}

    for item in source["locations"]:
        section = normalize_section(item["section"])
        if section not in grouped:
            continue
        counters[section] += 1
        local_images = []
        for image_index, image_url in enumerate(item.get("image_urls", []), start=1):
            local_images.append(download_image(image_url, section, counters[section], image_index))
        grouped[section].append(
            {
                "quantity": item.get("quantity"),
                "quantity_raw": item.get("quantity_raw"),
                "source_type": item.get("source_type", ""),
                "method": item.get("method", ""),
                "method_html": item.get("method_html", ""),
                "notes": item.get("notes", ""),
                "images": local_images,
            }
        )

    sections = []
    for section in TARGET_SECTIONS:
        items = grouped[section]
        sections.append(
            {
                "title": section,
                "item_count": len(items),
                "walnut_total": sum(item["quantity"] or 0 for item in items if isinstance(item.get("quantity"), int)),
                "entries": items,
            }
        )

    return {
        "title": source["page_title"],
        "source_url": source["source_url"],
        "generated_at": source["fetched_at"],
        "sections": sections,
        "rewards": [
            {
                "reward_name": item.get("reward_name", ""),
                "description": item.get("description", ""),
                "location": item.get("location", ""),
                "cost": item.get("cost"),
                "cost_raw": item.get("cost_raw", ""),
            }
            for item in source.get("rewards", [])
        ],
    }


def write_js(payload: dict) -> None:
    GUIDE_DIR.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    content = "window.GOLDEN_WALNUT_GUIDE_DATA = " + json.dumps(payload, ensure_ascii=False, indent=2) + ";\n"
    OUTPUT_JS.write_text(content, encoding="utf-8")


def main() -> int:
    GUIDE_DIR.mkdir(parents=True, exist_ok=True)
    source = load_source()
    payload = build_payload(source)
    write_js(payload)
    image_count = sum(len(section["entries"]) for section in payload["sections"])
    print(f"已写入: {OUTPUT_JS}")
    print(f"分组数: {len(payload['sections'])}")
    print(f"条目数: {image_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
