#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


DEFAULT_BLACKLIST = {
    "product_links": [],
    "shop_names": [],
    "keywords": [],
}


def load_blacklist(path: Path) -> dict:
    if not path.exists():
        return dict(DEFAULT_BLACKLIST)
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise SystemExit("Blacklist JSON must be an object.")
    merged = dict(DEFAULT_BLACKLIST)
    for key in DEFAULT_BLACKLIST:
        value = data.get(key, [])
        if not isinstance(value, list):
            raise SystemExit(f"Blacklist field '{key}' must be an array.")
        merged[key] = value
    return merged


def save_blacklist(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)


def add_unique(items: list[str], values: list[str]) -> list[str]:
    seen = {item.lower(): item for item in items if item}
    for value in values:
        normalized = value.strip()
        if not normalized:
            continue
        key = normalized.lower()
        if key not in seen:
            items.append(normalized)
            seen[key] = normalized
    return items


def remove_values(items: list[str], values: list[str]) -> list[str]:
    remove_keys = {value.strip().lower() for value in values if value.strip()}
    return [item for item in items if item.lower() not in remove_keys]


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage the persistent blacklist for Shopee YouYing selection.")
    parser.add_argument("--file", required=True, help="Blacklist JSON file to update.")
    parser.add_argument("--add-product-link", action="append", default=[], help="Add a blocked product link.")
    parser.add_argument("--add-shop-name", action="append", default=[], help="Add a blocked shop name.")
    parser.add_argument("--add-keyword", action="append", default=[], help="Add a blocked keyword.")
    parser.add_argument("--remove-product-link", action="append", default=[], help="Remove a blocked product link.")
    parser.add_argument("--remove-shop-name", action="append", default=[], help="Remove a blocked shop name.")
    parser.add_argument("--remove-keyword", action="append", default=[], help="Remove a blocked keyword.")
    parser.add_argument("--print", action="store_true", help="Print the final blacklist JSON to stdout.")
    args = parser.parse_args()

    path = Path(args.file)
    data = load_blacklist(path)

    data["product_links"] = add_unique(data["product_links"], args.add_product_link)
    data["shop_names"] = add_unique(data["shop_names"], args.add_shop_name)
    data["keywords"] = add_unique(data["keywords"], args.add_keyword)

    data["product_links"] = remove_values(data["product_links"], args.remove_product_link)
    data["shop_names"] = remove_values(data["shop_names"], args.remove_shop_name)
    data["keywords"] = remove_values(data["keywords"], args.remove_keyword)

    save_blacklist(path, data)

    if args.print:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
