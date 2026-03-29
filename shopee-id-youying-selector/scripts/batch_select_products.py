#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise SystemExit("Batch config JSON must be an object.")
    return data


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def build_output_name(prefix: str, start_date: str, end_date: str, suffix: str) -> str:
    return f"{prefix}_{start_date}_{end_date}.{suffix}"


def run_single(script_path: Path, config_path: Path) -> dict:
    command = [sys.executable, str(script_path), "--config", str(config_path)]
    completed = subprocess.run(command, capture_output=True, text=True, check=True)
    stdout = completed.stdout.strip()
    if not stdout:
        raise SystemExit("select_products.py returned no output.")
    return json.loads(stdout)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run multiple Shopee ID YouYing date-range jobs in batch.")
    parser.add_argument("--batch-config", required=True, help="JSON file describing shared settings and multiple date ranges.")
    args = parser.parse_args()

    batch_config_path = Path(args.batch_config)
    batch_config = load_json(batch_config_path)
    shared = batch_config.get("shared")
    runs = batch_config.get("runs")
    output_dir = Path(batch_config.get("output_dir", batch_config_path.parent / "batch-output"))
    filename_prefix = batch_config.get("filename_prefix", "shopee_id_otomotif")

    if not isinstance(shared, dict):
        raise SystemExit("batch config must contain an object field named 'shared'.")
    if not isinstance(runs, list) or not runs:
        raise SystemExit("batch config must contain a non-empty array field named 'runs'.")

    ensure_dir(output_dir)
    script_path = Path(__file__).with_name("select_products.py")
    results: list[dict] = []

    for run in runs:
        if not isinstance(run, dict):
            raise SystemExit("Each batch run entry must be an object.")
        start_date = run.get("start_date")
        end_date = run.get("end_date")
        if not start_date or not end_date:
            raise SystemExit("Each batch run entry must contain start_date and end_date.")

        merged = dict(shared)
        merged.update(run)
        merged["output"] = str(output_dir / build_output_name(filename_prefix, start_date, end_date, "xlsx"))
        merged["json_output"] = str(output_dir / build_output_name(filename_prefix, start_date, end_date, "json"))

        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            suffix=".json",
            prefix=f"{filename_prefix}_{start_date}_{end_date}_",
            delete=False,
        ) as handle:
            json.dump(merged, handle, ensure_ascii=False, indent=2)
            temp_config_path = Path(handle.name)

        try:
            run_result = run_single(script_path, temp_config_path)
            results.append(
                {
                    "start_date": start_date,
                    "end_date": end_date,
                    "output": merged["output"],
                    "json_output": merged["json_output"],
                    "count": run_result["count"],
                }
            )
        finally:
            if temp_config_path.exists():
                temp_config_path.unlink()

    summary_path = output_dir / f"{filename_prefix}_batch_summary.json"
    with summary_path.open("w", encoding="utf-8") as handle:
        json.dump(results, handle, ensure_ascii=False, indent=2)

    print(json.dumps({"summary": str(summary_path), "runs": len(results)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
