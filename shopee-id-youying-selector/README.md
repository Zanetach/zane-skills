# shopee-id-youying-selector

Native AI skill for selecting Shopee Indonesia products from YouYing Data.

## What It Does

- Logs into `youyingshuju.com`
- Queries Shopee Indonesia product data
- Filters `Otomotif` products by date range, sales, price, and rating
- Excludes Mall or Official-style listings based on configurable filter modes
- Exports fixed-format Excel and optional JSON
- Supports batch runs, merge, dedupe, and blacklist workflows

## Quick Prompt

```text
Use $shopee-id-youying-selector.
友鹰账号：<账号>
友鹰密码：<密码>
时间范围：2025-09-28 到 2026-03-27
按件数降序，筛选 Shopee 印尼 Otomotif 类目前10个产品，排除 Shopee Mall 和评分低于 4.7 的商品，导出 Excel。
```

## Entry Points

- Main instructions: [`SKILL.md`](./SKILL.md)
- Native metadata: [`agents/openai.yaml`](./agents/openai.yaml)
- Main script: [`scripts/select_products.py`](./scripts/select_products.py)

## Notes

- Example configs intentionally do not contain real credentials.
- Runtime result files should stay out of Git.
