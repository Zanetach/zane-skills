# shopee-id-youying-selector

Native AI skill for selecting Shopee Indonesia products from YouYing Data.

## What It Does

- Logs into `youyingshuju.com`
- Queries Shopee Indonesia product data
- Filters `Otomotif` products by date range, sales, price, and rating
- Excludes Mall or Official-style listings based on configurable filter modes
- Exports fixed-format Excel and optional JSON
- Supports batch runs, merge, dedupe, and blacklist workflows

## Entry Points

- Main instructions: [`SKILL.md`](./SKILL.md)
- Native metadata: [`agents/openai.yaml`](./agents/openai.yaml)
- Main script: [`scripts/select_products.py`](./scripts/select_products.py)

## Notes

- Example configs intentionally do not contain real credentials.
- Runtime result files should stay out of Git.
