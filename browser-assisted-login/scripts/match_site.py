#!/opt/homebrew/bin/python3
import argparse
import json
import sys
from pathlib import Path
from urllib.parse import urlparse


def normalize_host(value: str) -> str:
    value = value.strip()
    if "://" in value:
        value = urlparse(value).netloc
    return value.lower()


def load_sites(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    sites = data.get("sites")
    if not isinstance(sites, list):
        raise ValueError("config file must contain a top-level 'sites' list")
    return sites


def score_site(site: dict, host: str) -> tuple[int, int]:
    matches = site.get("match", [])
    if not isinstance(matches, list):
        return (-1, -1)

    best = (-1, -1)
    for candidate in matches:
        if not isinstance(candidate, str):
            continue
        normalized = candidate.lower()
        if host == normalized:
            best = max(best, (3, len(normalized)))
        elif host.endswith("." + normalized):
            best = max(best, (2, len(normalized)))
        elif normalized in host:
            best = max(best, (1, len(normalized)))
    return best


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Match a login site config by URL or hostname."
    )
    parser.add_argument("--config", required=True, help="Path to site config JSON")
    parser.add_argument("--url", required=True, help="Target URL or hostname")
    args = parser.parse_args()

    config_path = Path(args.config)
    host = normalize_host(args.url)

    try:
        sites = load_sites(config_path)
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1

    ranked: list[tuple[tuple[int, int], dict]] = []
    for site in sites:
        score = score_site(site, host)
        if score[0] >= 0:
            ranked.append((score, site))

    if not ranked:
        print(
            json.dumps(
                {"matched": False, "host": host, "reason": "no matching site config"},
                ensure_ascii=False,
                indent=2,
            )
        )
        return 2

    ranked.sort(key=lambda item: item[0], reverse=True)
    best_score, best_site = ranked[0]
    print(
        json.dumps(
            {
                "matched": True,
                "host": host,
                "match_score": {
                    "tier": best_score[0],
                    "length": best_score[1],
                },
                "site": best_site,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
