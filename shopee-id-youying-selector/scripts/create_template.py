#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from openpyxl import Workbook


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a blank Excel template workbook.")
    parser.add_argument("--columns", required=True, help="JSON file containing the ordered column names.")
    parser.add_argument("--output", required=True, help="Output .xlsx path.")
    args = parser.parse_args()

    columns_path = Path(args.columns)
    output_path = Path(args.output)

    with columns_path.open("r", encoding="utf-8") as handle:
        columns = json.load(handle)

    if not isinstance(columns, list) or not all(isinstance(column, str) for column in columns):
        raise SystemExit("Columns JSON must be an array of strings.")

    wb = Workbook()
    ws = wb.active
    ws.title = "products"
    ws.append(columns)
    wb.save(output_path)
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
