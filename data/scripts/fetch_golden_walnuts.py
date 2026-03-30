#!/usr/bin/env python3
"""
抓取中文 Stardew Valley Wiki 的“金色核桃”页面，并提取结构化数据。
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple
from urllib.parse import urljoin
from urllib.request import Request, urlopen


DEFAULT_URL = "https://zh.stardewvalleywiki.com/%E9%87%91%E8%89%B2%E6%A0%B8%E6%A1%83"
DEFAULT_OUTPUT = (
    Path("/Users/edisonzhang/Documents/Projects/stardew_tools")
    / "data"
    / "processed"
    / "golden_walnuts_zh.json"
)
API_TEMPLATE = (
    "https://zh.stardewvalleywiki.com/mediawiki/api.php"
    "?action=parse&page=%E9%87%91%E8%89%B2%E6%A0%B8%E6%A1%83&prop=text&formatversion=2&format=json"
)
USER_AGENT = "stardew-tools-golden-walnuts-fetcher/1.0"


@dataclass
class Node:
    tag: str
    attrs: Dict[str, str] = field(default_factory=dict)
    children: List["Node"] = field(default_factory=list)
    data: str = ""
    parent: Optional["Node"] = None

    def append_child(self, child: "Node") -> None:
        child.parent = self
        self.children.append(child)

    def iter_children(self, tags: Optional[Tuple[str, ...]] = None) -> Iterable["Node"]:
        for child in self.children:
            if child.tag == "#text":
                continue
            if tags is None or child.tag in tags:
                yield child

    def classes(self) -> List[str]:
        value = self.attrs.get("class", "")
        return [item for item in value.split() if item]


class TreeBuilder(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = Node("document")
        self.stack = [self.root]

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        node = Node(tag=tag, attrs={k: v or "" for k, v in attrs})
        self.stack[-1].append_child(node)
        self.stack.append(node)

    def handle_startendtag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        node = Node(tag=tag, attrs={k: v or "" for k, v in attrs})
        self.stack[-1].append_child(node)

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                break

    def handle_data(self, data: str) -> None:
        if not data:
            return
        self.stack[-1].append_child(Node(tag="#text", data=data))


def fetch_text(url: str) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", "replace")


def fetch_via_api() -> Tuple[str, str, str]:
    payload = json.loads(fetch_text(API_TEMPLATE))
    parse = payload["parse"]
    return parse["text"], parse["title"], "mediawiki_api"


def fetch_via_html(url: str) -> Tuple[str, str, str]:
    return fetch_text(url), "金色核桃", "page_html"


def build_tree(markup: str) -> Node:
    parser = TreeBuilder()
    parser.feed(markup)
    parser.close()
    return parser.root


def normalize_space(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = re.sub(r"\[[0-9]+\]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def text_content(node: Node, skip_tags: Tuple[str, ...] = ("style", "script")) -> str:
    if node.tag == "#text":
        return node.data
    if node.tag in skip_tags:
        return ""
    return "".join(text_content(child, skip_tags=skip_tags) for child in node.children)


def heading_text(node: Node) -> str:
    text = normalize_space(text_content(node))
    text = text.replace("[编辑]", "").replace("[e]", "")
    return normalize_space(text)


def find_first(node: Node, predicate) -> Optional[Node]:
    if predicate(node):
        return node
    for child in node.children:
        found = find_first(child, predicate)
        if found is not None:
            return found
    return None


def find_content_root(root: Node) -> Node:
    mw_content = find_first(
        root,
        lambda n: n.attrs.get("id") == "mw-content-text" or "mw-parser-output" in n.classes(),
    )
    if mw_content is None:
        return root
    parser_output = find_first(mw_content, lambda n: "mw-parser-output" in n.classes())
    return parser_output or mw_content


def is_hidden(node: Node) -> bool:
    classes = set(node.classes())
    if {"mw-editsection", "reference", "sortkey"} & classes:
        return True
    style = node.attrs.get("style", "")
    return "display:none" in style.replace(" ", "").lower()


def collect_images(node: Node, page_url: str) -> List[str]:
    images: List[str] = []

    def walk(current: Node) -> None:
        if current.tag == "img":
            src = current.attrs.get("src")
            if src:
                images.append(urljoin(page_url, src))
        for child in current.children:
            walk(child)

    walk(node)
    deduped: List[str] = []
    seen = set()
    for item in images:
        if item not in seen:
            deduped.append(item)
            seen.add(item)
    return deduped


def collect_links(node: Node, page_url: str) -> List[Dict[str, str]]:
    links: List[Dict[str, str]] = []

    def walk(current: Node) -> None:
        if current.tag == "a":
            href = current.attrs.get("href")
            text = normalize_space(text_content(current))
            if href and text:
                links.append({"text": text, "href": urljoin(page_url, href)})
        for child in current.children:
            walk(child)

    walk(node)
    deduped: List[Dict[str, str]] = []
    seen = set()
    for item in links:
        key = (item["text"], item["href"])
        if key not in seen:
            deduped.append(item)
            seen.add(key)
    return deduped


ALLOWED_HTML_TAGS = {"a", "b", "strong", "i", "em", "br", "ul", "ol", "li", "span"}


def simplified_html(node: Node, page_url: str) -> str:
    def render(current: Node) -> str:
        if current.tag == "#text":
            return html.escape(current.data)
        if is_hidden(current) or current.tag in {"style", "script", "table"}:
            return ""
        if current.tag == "img":
            return ""
        body = "".join(render(child) for child in current.children)
        if current.tag not in ALLOWED_HTML_TAGS:
            return body
        attrs = ""
        if current.tag == "a":
            href = current.attrs.get("href")
            if href:
                attrs = f' href="{html.escape(urljoin(page_url, href), quote=True)}"'
        return f"<{current.tag}{attrs}>{body}</{current.tag}>"

    rendered = render(node)
    rendered = re.sub(r"(?:\s*<br>\s*){2,}", "<br>", rendered)
    return rendered.strip()


def extract_notes(node: Node) -> str:
    notes: List[str] = []

    def walk(current: Node) -> None:
        if current.tag in {"sup", "small"}:
            text = normalize_space(text_content(current))
            if text:
                notes.append(text)
        for child in current.children:
            walk(child)

    walk(node)
    deduped: List[str] = []
    seen = set()
    for item in notes:
        if item not in seen:
            deduped.append(item)
            seen.add(item)
    return " ".join(deduped)


def get_table_rows(table: Node) -> List[List[Node]]:
    pending: Dict[int, Dict[str, object]] = {}
    rows: List[List[Node]] = []
    tr_nodes = [node for node in table.iter_children() if node.tag in {"thead", "tbody"}]
    if tr_nodes:
        expanded: List[Node] = []
        for container in tr_nodes:
            expanded.extend(child for child in container.iter_children(("tr",)))
        tr_nodes = expanded
    else:
        tr_nodes = [child for child in table.iter_children(("tr",))]

    for tr in tr_nodes:
        row: List[Node] = []
        col = 0
        cells = [child for child in tr.iter_children() if child.tag in {"th", "td"}]
        cell_index = 0
        while cell_index < len(cells) or pending:
            while col in pending:
                row.append(pending[col]["cell"])  # type: ignore[arg-type]
                pending[col]["rows_left"] = int(pending[col]["rows_left"]) - 1
                if int(pending[col]["rows_left"]) <= 0:
                    del pending[col]
                col += 1
            if cell_index >= len(cells):
                if not pending:
                    break
                col = min(pending)
                continue
            cell = cells[cell_index]
            cell_index += 1
            colspan = max(1, int(cell.attrs.get("colspan", "1") or "1"))
            rowspan = max(1, int(cell.attrs.get("rowspan", "1") or "1"))
            for offset in range(colspan):
                row.append(cell)
                if rowspan > 1:
                    pending[col + offset] = {"cell": cell, "rows_left": rowspan - 1}
            col += colspan
        if row:
            rows.append(row)
    return rows


def semantic_header(header: str) -> Optional[str]:
    compact = normalize_space(header).replace(" ", "")
    if "数量" in compact:
        return "quantity"
    if "来源类型" in compact:
        return "source_type"
    if "获得方式" in compact:
        return "method"
    if "图片" in compact:
        return "image"
    if "奖励" in compact:
        return "reward_name"
    if "花费" in compact or "价格" in compact or "成本" in compact:
        return "cost"
    if "说明" in compact or "描述" in compact:
        return "description"
    if "位置" in compact:
        return "location"
    return None


def parse_int(text: str) -> Optional[int]:
    if not text:
        return None
    match = re.search(r"\d+", text)
    if not match:
        return None
    return int(match.group(0))


def normalize_context_title(text: str) -> str:
    text = normalize_space(text)
    return re.sub(r"\s*（共.*?）$", "", text)


def maybe_context_paragraph(node: Node) -> Optional[str]:
    if node.tag != "p":
        return None
    text = normalize_space(text_content(node))
    if not text:
        return None
    if len(text) > 40:
        return None
    if "：" in text or "共" in text or text.endswith("区") or text.endswith("区域"):
        return normalize_context_title(text.rstrip("："))
    return None


def analyze_table(rows: List[List[Node]], required_keys: set[str]) -> Tuple[Optional[str], Optional[int], Dict[str, int]]:
    table_title: Optional[str] = None
    for index, row in enumerate(rows[:3]):
        header_map: Dict[str, int] = {}
        semantic_count = 0
        for col_index, cell in enumerate(row):
            key = semantic_header(text_content(cell))
            if key is not None and key not in header_map:
                header_map[key] = col_index
                semantic_count += 1
        if required_keys.issubset(header_map):
            if index > 0:
                title_text = normalize_context_title(normalize_space(text_content(rows[index - 1][0])))
                if title_text:
                    table_title = title_text
            return table_title, index, header_map
    return None, None, {}


def parse_location_table(
    table: Node,
    page_url: str,
    section: Optional[str],
    subsection: Optional[str],
    warnings: List[str],
) -> List[Dict[str, object]]:
    rows = get_table_rows(table)
    if not rows:
        return []
    required = {"quantity", "source_type", "method"}
    table_title, header_index, header_map = analyze_table(rows, required)
    if header_index is None:
        warnings.append(f"跳过无法识别的地点表格，表头={list(header_map.keys())}")
        return []

    effective_section = section
    effective_subsection = subsection
    if table_title:
        if not effective_section:
            effective_section = table_title
        elif effective_section != table_title:
            if "：" in effective_section or "共" in effective_section:
                effective_section = table_title
            elif not effective_subsection:
                effective_subsection = table_title

    parsed_rows: List[Dict[str, object]] = []
    for row in rows[header_index + 1 :]:
        if all(cell.tag == "th" for cell in row):
            continue
        method_index = header_map["method"]
        if method_index >= len(row):
            continue
        quantity_text = normalize_space(text_content(row[header_map["quantity"]]))
        source_type_text = normalize_space(text_content(row[header_map["source_type"]]))
        method_cell = row[method_index]
        method_text = normalize_space(text_content(method_cell))
        if not method_text:
            continue
        image_cell = row[header_map["image"]] if "image" in header_map and header_map["image"] < len(row) else method_cell
        quantity_value = parse_int(quantity_text)
        entry: Dict[str, object] = {
            "section": effective_section or "",
            "subsection": effective_subsection,
            "quantity": quantity_value,
            "source_type": source_type_text,
            "method": method_text,
            "method_html": simplified_html(method_cell, page_url),
            "image_urls": collect_images(image_cell, page_url),
            "notes": extract_notes(method_cell),
            "links": collect_links(method_cell, page_url),
        }
        if quantity_value is None:
            entry["quantity_raw"] = quantity_text
        parsed_rows.append(entry)
    return parsed_rows


def parse_reward_table(table: Node, page_url: str, warnings: List[str]) -> List[Dict[str, object]]:
    rows = get_table_rows(table)
    if not rows:
        return []
    required = {"reward_name", "cost", "description"}
    _, header_index, header_map = analyze_table(rows, required)
    if header_index is None:
        warnings.append(f"跳过无法识别的奖励表格，表头={list(header_map.keys())}")
        return []

    rewards: List[Dict[str, object]] = []
    for row in rows[header_index + 1 :]:
        reward_name = normalize_space(text_content(row[header_map["reward_name"]])) if header_map["reward_name"] < len(row) else ""
        cost_text = normalize_space(text_content(row[header_map["cost"]])) if header_map["cost"] < len(row) else ""
        description_cell = row[header_map["description"]] if header_map["description"] < len(row) else None
        location_text = normalize_space(text_content(row[header_map["location"]])) if "location" in header_map and header_map["location"] < len(row) else ""
        if not reward_name:
            continue
        rewards.append(
            {
                "reward_name": reward_name,
                "cost": parse_int(cost_text),
                "cost_raw": cost_text,
                "description": normalize_space(text_content(description_cell)) if description_cell else "",
                "location": location_text,
                "image_urls": collect_images(row[header_map["image"]], page_url)
                if "image" in header_map and header_map["image"] < len(row)
                else [],
            }
        )
    return rewards


def parse_document(markup: str, page_url: str, parse_source: str) -> Dict[str, object]:
    root = build_tree(markup)
    content_root = find_content_root(root)
    children = list(content_root.iter_children())

    locations: List[Dict[str, object]] = []
    rewards: List[Dict[str, object]] = []
    warnings: List[str] = []

    mode: Optional[str] = None
    current_h3: Optional[str] = None
    current_h4: Optional[str] = None
    pending_context: Optional[str] = None

    for child in children:
        if child.tag == "h2":
            title = heading_text(child)
            current_h3 = None
            current_h4 = None
            pending_context = None
            if title == "金色核桃位置":
                mode = "locations"
            elif title == "兑换奖励":
                mode = "rewards"
            else:
                mode = None
            continue

        if mode is None:
            continue

        if child.tag == "h3":
            current_h3 = normalize_context_title(heading_text(child))
            current_h4 = None
            pending_context = None
            continue

        if child.tag == "h4":
            current_h4 = normalize_context_title(heading_text(child))
            pending_context = None
            continue

        paragraph_context = maybe_context_paragraph(child)
        if paragraph_context is not None:
            pending_context = paragraph_context
            continue

        if child.tag != "table":
            continue

        if mode == "locations":
            if "wikitable" not in child.classes():
                continue
            section = current_h3 or pending_context or ""
            subsection = current_h4
            parsed_locations = parse_location_table(child, page_url, section, subsection, warnings)
            if parsed_locations and any(not item.get("section") for item in parsed_locations):
                warnings.append("发现没有 section 上下文的位置表格")
            locations.extend(parsed_locations)
            pending_context = None
        elif mode == "rewards":
            rewards.extend(parse_reward_table(child, page_url, warnings))

    return {
        "locations": locations,
        "rewards": rewards,
        "warnings": warnings,
        "parse_source": parse_source,
    }


def validate_result(payload: Dict[str, object]) -> List[str]:
    errors: List[str] = []
    locations = payload["locations"]
    rewards = payload["rewards"]
    if not isinstance(locations, list) or not locations:
        errors.append("locations 为空")
    if not isinstance(rewards, list) or not rewards:
        errors.append("rewards 为空")

    for index, item in enumerate(locations if isinstance(locations, list) else []):
        if not item.get("section") or not item.get("method"):
            errors.append(f"locations[{index}] 缺少 section 或 method")
        for image_url in item.get("image_urls", []):
            if not isinstance(image_url, str) or not image_url.startswith("http"):
                errors.append(f"locations[{index}] 存在非绝对图片链接")
                break
    for index, item in enumerate(rewards if isinstance(rewards, list) else []):
        for image_url in item.get("image_urls", []):
            if not isinstance(image_url, str) or not image_url.startswith("http"):
                errors.append(f"rewards[{index}] 存在非绝对图片链接")
                break
    return errors


def build_output(
    source_url: str,
    page_title: str,
    parsed: Dict[str, object],
    validation_errors: List[str],
) -> Dict[str, object]:
    locations = parsed["locations"]
    rewards = parsed["rewards"]
    quantity_sum = sum(
        item["quantity"] for item in locations if isinstance(item.get("quantity"), int)
    )
    return {
        "source_url": source_url,
        "page_title": page_title,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "locations": locations,
        "rewards": rewards,
        "meta": {
            "parse_source": parsed["parse_source"],
            "location_count": len(locations),
            "reward_count": len(rewards),
            "quantity_sum": quantity_sum,
            "warnings": parsed["warnings"],
            "validation_errors": validation_errors,
        },
    }


def write_json(payload: Dict[str, object], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="抓取金色核桃页面并输出结构化 JSON")
    parser.add_argument("--url", default=DEFAULT_URL, help="目标页面 URL")
    parser.add_argument("--out", default=str(DEFAULT_OUTPUT), help="输出 JSON 路径")
    parser.add_argument(
        "--force-html",
        action="store_true",
        help="跳过 MediaWiki API，直接抓取页面 HTML",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = Path(args.out).expanduser().resolve()

    fetch_errors: List[str] = []
    try:
        if args.force_html:
            markup, page_title, parse_source = fetch_via_html(args.url)
        else:
            try:
                markup, page_title, parse_source = fetch_via_api()
            except Exception as exc:
                fetch_errors.append(f"API 抓取失败，回退 HTML: {exc}")
                markup, page_title, parse_source = fetch_via_html(args.url)
    except Exception as exc:
        print(f"抓取失败: {exc}", file=sys.stderr)
        return 1

    parsed = parse_document(markup, args.url, parse_source)
    parsed["warnings"] = fetch_errors + list(parsed["warnings"])
    validation_errors = validate_result(parsed)
    payload = build_output(args.url, page_title, parsed, validation_errors)
    write_json(payload, output_path)

    print(f"已写入: {output_path}")
    print(f"解析来源: {payload['meta']['parse_source']}")
    print(f"位置条目: {payload['meta']['location_count']}")
    print(f"奖励条目: {payload['meta']['reward_count']}")
    print(f"数量总和: {payload['meta']['quantity_sum']}")
    if payload["meta"]["warnings"]:
        print("警告:")
        for warning in payload["meta"]["warnings"]:
            print(f"  - {warning}")
    if validation_errors:
        print("校验失败:")
        for error in validation_errors:
            print(f"  - {error}")
        return 2
    print("校验通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
