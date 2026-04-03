# youying-selector

Native AI skill for selecting Shopee site products from YouYing Data. Default site: Indonesia.

## What It Does

- Logs into `youyingshuju.com`
- Queries Shopee site product data
- Filters category products by date range, sales, price, and rating. Default category: `Otomotif`
- Excludes Mall or Official-style listings based on configurable filter modes
- Exports fixed-format Excel and optional JSON
- Supports batch runs, merge, dedupe, and blacklist workflows

## Supported Filters

Common configurable filters include:

- site
- category
- date range
- minimum monthly sales
- minimum price
- minimum rating
- output limit
- Mall filter mode

## Supported Sites

Built-in confirmed presets currently include:

- Malaysia
- Indonesia
- Thailand
- Philippines
- Taiwan
- Singapore
- Vietnam
- Brazil
- Chile
- Mexico
- Columbia

## Quick Prompt

```text
Use $shopee-id-youying-selector.
友鹰账号：<账号>
友鹰密码：<密码>
站点：菲律宾
类目：Beauty
时间范围：2025-09-28 到 2026-03-27
按件数降序，筛选 Shopee 站点类目前10个产品，排除 Shopee Mall 和评分低于 4.7 的商品，导出 Excel。
```

Complex example:

```text
Use $shopee-id-youying-selector.
友鹰账号：<账号>
友鹰密码：<密码>
站点：菲律宾
类目：Beauty
时间范围：2025-10-01 到 2026-03-27
最低月销：200
最低价格：120000 IDR
最低评分：4.8
Mall过滤模式：strict
输出前20个产品
导出 Excel 和 JSON。
```

## Entry Points

- Main instructions: [`SKILL.md`](./SKILL.md)
- Native metadata: [`agents/openai.yaml`](./agents/openai.yaml)
- Main script: [`scripts/select_products.py`](./scripts/select_products.py)

## Notes

- Example configs intentionally do not contain real credentials.
- Runtime result files should stay out of Git.
