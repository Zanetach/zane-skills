#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

from openpyxl import Workbook


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def infer_columns(rows: Iterable[dict]) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row.keys():
            if key not in seen:
                seen.add(key)
                ordered.append(key)
    return ordered


def autosize_columns(ws) -> None:
    for column_cells in ws.columns:
        values = ["" if cell.value is None else str(cell.value) for cell in column_cells]
        width = min(max(len(value) for value in values) + 2, 60)
        ws.column_dimensions[column_cells[0].column_letter].width = width


def write_workbook(rows: list[dict], columns: list[str], output_path: Path) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "products"

    ws.append(columns)
    for row in rows:
        ws.append([row.get(column, "") for column in columns])

    autosize_columns(ws)
    wb.save(output_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Export product rows to Excel.")
    parser.add_argument("--input", required=True, help="Input JSON file containing row objects.")
    parser.add_argument("--output", required=True, help="Output .xlsx path.")
    parser.add_argument(
        "--columns",
        help="Optional JSON file containing an array of column names in the desired order.",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    rows = load_json(input_path)
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        raise SystemExit("Input JSON must be an array of objects.")

    if args.columns:
        columns = load_json(Path(args.columns))
        if not isinstance(columns, list) or not all(isinstance(column, str) for column in columns):
            raise SystemExit("Columns JSON must be an array of strings.")
    else:
        columns = infer_columns(rows)

    write_workbook(rows, columns, output_path)
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
