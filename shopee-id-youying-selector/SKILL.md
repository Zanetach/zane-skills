---
name: shopee-id-youying-selector
description: Automate product selection on YouYing Data for Shopee sites, defaulting to Indonesia. Use when the user wants to log into youyingshuju.com, choose a Shopee site, filter a category, apply sales/price/date constraints, exclude Shopee Mall and low-rating items, and export the top products to Excel.
---

# Shopee ID YouYing Selector

Use this skill when the task is to automate YouYing Data product selection for Shopee and export the result to Excel. The default site preset is Indonesia.

## Scope

This workflow targets the user's current default rule set:

- Data source: `友鹰数据`
- Platform: `Shopee`
- Site: `印度尼西亚`
- Category: `Otomotif` by default, but overrideable per run
- Minimum monthly sales: `50`
- Minimum price: `80000 IDR`
- Listing age: `recent half year`
- Sort: by sales quantity descending
- Exclusions:
  - `Shopee Mall`
  - rating `< 4.7`
- Output: first `10` qualifying products

## Required Inputs

Collect these before running:

1. Login state for `https://www.youyingshuju.com/index.html#/`
2. A date range from the user
3. Output path for the workbook

## Runtime Parameters

Unless the user overrides them, use these defaults:

- `platform`: `Shopee`
- `site`: `印度尼西亚`
- `country_code`: `2`
- `category_tree_country`: `Indonesia`
- `category`: `Otomotif` by default
- `min_monthly_sales`: `50`
- `min_price_idr`: `80000`
- `min_rating`: `4.7`
- `exclude_shopee_mall`: `true`
- `mall_filter_mode`: `custom`
- `sort_by`: `sales quantity desc`
- `limit`: `10`

The date range must always come from the user input for that run:

- `start_date`
- `end_date`

The category is also runtime-configurable:

- `category_keyword`

More filter conditions are also runtime-configurable:

- `min_monthly_sales`
- `min_price`
- `min_rating`
- `limit`
- `mall_filter_mode`
- `mall_keywords`
- `mall_exclude_keywords`
- `max_pages`
- `request_retry_limit`
- `run_retry_limit`

For non-Indonesia sites, also provide:

- `site`
- `site_presets_file` if you want reusable custom presets
- `site_label`
- `country_code`
- `category_tree_country`

Current built-in preset:

- `Indonesia` / `印度尼西亚` / `印尼`
- `Thailand` / `泰国`
- `Philippines` / `菲律宾`
- `Malaysia` / `马来西亚`
- `Singapore` / `新加坡`
- `Vietnam` / `越南`
- `Taiwan` / `台湾`
- `Brazil` / `巴西`
- `Mexico` / `墨西哥`
- `Columbia` / `哥伦比亚`
- `Poland` / `波兰`
- `Chile` / `智利`

Notes:

- `Indonesia` currently has a confirmed built-in `country_code=2`
- `Malaysia` currently has a confirmed built-in `country_code=1`
- `Thailand` currently has a confirmed built-in `country_code=3`
- `Philippines` currently has a confirmed built-in `country_code=4`
- `Taiwan` currently has a confirmed built-in `country_code=5`
- `Singapore` currently has a confirmed built-in `country_code=6`
- `Vietnam` currently has a confirmed built-in `country_code=7`
- `Brazil` currently has a confirmed built-in `country_code=8`
- `Chile` currently has a confirmed built-in `country_code=9`
- `Mexico` currently has a confirmed built-in `country_code=11`
- `Columbia` currently has a confirmed built-in `country_code=12`
- `Poland` currently only has a confirmed public category path; if it appears in your live menu, still verify its `country_code` before first use

For other Shopee sites outside this list, pass explicit `country_code` and `category_tree_country`, or register them in a custom site presets JSON file.

For Mall filtering, support these modes:

- `strict`: only exclude results that look explicitly like `Shopee Mall`
- `loose`: exclude any result that looks like `Mall` or `Official`
- `custom`: use configurable keyword lists
- `none`: do not exclude on Mall/Official terms

Recommended default:

- use `custom` with the `custom-safe` preset unless the business rule has been finalized

## Credential Handling

Prefer one of these approaches, in this order:

1. Manual login once with a persistent browser profile
2. Existing authenticated browser session reused via profile or storage state
3. One-time credentials provided by the user in chat only if they accept that risk

Do not store plaintext credentials in repo files.
Do not commit browser state, cookies, or exported business data unless the user explicitly asks.

## Dialog-Only Usage

If the environment has no terminal access and only exposes an AI chat box, the user can provide credentials and runtime parameters directly in the conversation.

Quick prompt:

```text
Use $shopee-id-youying-selector.
友鹰账号：<账号>
友鹰密码：<密码>
站点：菲律宾
类目：Beauty
时间范围：2025-09-28 到 2026-03-27
按件数降序，筛选前10个产品，排除 Shopee Mall 和评分低于 4.7 的商品，导出 Excel。
```

Complex filter example:

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

Recommended dialog format:

```text
Use $shopee-id-youying-selector.
友鹰账号：<username>
友鹰密码：<password>
站点：菲律宾
类目：Beauty
时间范围：2025-09-28 到 2026-03-27
输出路径：/tmp/result.xlsx
```

In dialog-only environments:

- treat the provided username and password as one-time credentials for the current run
- do not write the credentials into repo files, examples, or persistent config files
- prefer returning the generated file path back to the user after completion
- warn briefly that credentials shared in chat may remain in conversation history

## Recommended Login Workflow

For the safest recurring setup, have the user log in once with a persistent profile, then reuse it:

```bash
agent-browser --profile /tmp/youying-profile open https://www.youyingshuju.com/index.html#/
```

After manual login completes, future runs can reuse the same profile without asking for the password again.

## Execution Workflow

1. Open the site and confirm login state.
2. Navigate to the Shopee data area.
3. Switch site to the requested Shopee site. Default: `印度尼西亚`.
4. Set the requested category. Default: `Otomotif`.
5. Apply filters for monthly sales, price, and recent half-year listing window.
6. Sort by sales quantity descending.
7. Inspect each candidate in order and reject:
   - Shopee Mall items
   - items with rating below `4.7`
8. Stop after collecting `10` valid products.
9. Normalize the rows to the user-defined Excel columns.
10. Export with `scripts/export_excel.py`.

## Notes On Date Range

If the site exposes a built-in `近半年` filter, use that directly.
If the site requires explicit dates, confirm the platform's exact semantics before hardcoding the range. Do not assume that "half year" means a fixed `180` days unless the product logic is confirmed.

## Default Excel Columns

If the user does not provide an existing Excel sample, use this column order:

1. `产品名称`
2. `产品链接`
3. `站点`
4. `类目`
5. `月销量`
6. `价格(IDR)`
7. `评分`
8. `是否Shopee Mall`
9. `上架时间`
10. `店铺名称`
11. `筛选结果`
12. `淘汰原因`
13. `抓取日期`

## Expected Data Shape

Prepare a JSON array of row objects before export. Example:

```json
[
  {
    "产品名称": "Example item",
    "产品链接": "https://shopee.co.id/...",
    "站点": "印度尼西亚",
    "类目": "Otomotif",
    "月销量": 320,
    "价格(IDR)": 125000,
    "评分": 4.9,
    "是否Shopee Mall": "否",
    "上架时间": "2026-02-10",
    "店铺名称": "Example Shop",
    "筛选结果": "入选",
    "淘汰原因": "",
    "抓取日期": "2026-03-29"
  }
]
```

## Export

Use:

```bash
python3 scripts/export_excel.py --input rows.json --output result.xlsx
```

If the user provides a fixed column order, pass `--columns columns.json`.
Otherwise use `examples/columns.default.json`.

## End-To-End Run

Use the integrated script when you want to log in, query, and export in one step:

```bash
python3 scripts/select_products.py \
  --username 'YOUR_USERNAME' \
  --password 'YOUR_PASSWORD' \
  --site 'Indonesia' \
  --start-date '2025-09-28' \
  --end-date '2026-03-27' \
  --output examples/result.xlsx \
  --json-output examples/result.json
```

Or use a fixed config file:

```bash
python3 scripts/select_products.py --config examples/run-config.sample.json
```

The preset configs under `examples/run-config.strict.json`, `examples/run-config.loose.json`, and `examples/run-config.custom-safe.json` intentionally omit credentials. Pair them with environment variables or provide `--username` and `--password` at runtime.

If you want a non-`Otomotif` example, use:

```bash
python3 scripts/select_products.py --config examples/run-config.beauty.sample.json
```

To add non-default site presets, use:

```json
{
  "Thailand": {
    "site_name": "Thailand",
    "site_label": "泰国",
    "country_code": 999,
    "category_tree_country": "Thailand"
  }
}
```

The bundled [examples/site-presets.sample.json](/Users/zane/Documents/Coderepo/skills/shopee-id-youying-selector/examples/site-presets.sample.json) uses placeholder values like `999`. Replace them with confirmed values from your own YouYing environment before running.

For safer credential handling, prefer environment variables:

```bash
YOUYING_USERNAME='YOUR_USERNAME' \
YOUYING_PASSWORD='YOUR_PASSWORD' \
python3 scripts/select_products.py \
  --site 'Indonesia' \
  --start-date '2025-09-28' \
  --end-date '2026-03-27' \
  --output examples/result.xlsx \
  --json-output examples/result.json
```

The integrated script also supports:

- `--max-pages`: cap how many API pages are scanned
- `--request-retry-limit`: retry count for each API request
- `--run-retry-limit`: full-run retry count with automatic re-login
- `--site`: Shopee site preset, default `Indonesia`
- `--site-presets-file`: custom site preset JSON
- `--site-label`: label written into the Excel output
- `--country-code`: explicit YouYing API country code for non-default sites
- `--category-tree-country`: explicit category JSON country segment for non-default sites
- `--mall-filter-mode`: `strict | loose | custom | none`
- `--mall-keywords`: custom blocked keywords
- `--mall-exclude-keywords`: custom allowlist keywords

## Batch Run

Use the batch runner when you want to execute multiple date ranges in one command:

```bash
python3 scripts/batch_select_products.py --batch-config examples/batch-config.sample.json
```

The batch config contains:

- `shared`: login and shared filter settings
- `runs`: an array of `{start_date, end_date}` objects
- `output_dir`: where all outputs are written
- `filename_prefix`: filename prefix for generated Excel/JSON files

## Merge Batch Results

Use the merge script when you want one workbook that combines every batch result:

```bash
python3 scripts/merge_batch_results.py \
  --summary-json examples/batch-output/shopee_id_otomotif_batch_batch_summary.json \
  --output examples/batch-output/shopee_id_otomotif_batch_merged.xlsx
```

You can also deduplicate and apply a blacklist:

```bash
python3 scripts/merge_batch_results.py \
  --summary-json examples/batch-output/shopee_id_otomotif_batch_batch_summary.json \
  --output examples/batch-output/shopee_id_otomotif_batch_merged.xlsx \
  --blacklist-json examples/blacklist.sample.json \
  --dedupe-by product_link
```

To maintain a long-term blacklist without hand-editing JSON:

```bash
python3 scripts/manage_blacklist.py \
  --file examples/blacklist.persistent.json \
  --add-shop-name 'Moto_Xpert' \
  --add-keyword 'ebook' \
  --print
```

## Files

- `scripts/export_excel.py`: write normalized rows into `.xlsx`
- `scripts/create_template.py`: generate a blank template workbook
- `scripts/select_products.py`: log into YouYing, query Shopee site products, and export the fixed Excel format
- `scripts/batch_select_products.py`: run multiple date-range jobs and export one Excel/JSON pair per range
- `scripts/merge_batch_results.py`: merge multiple batch outputs into one workbook
- `scripts/manage_blacklist.py`: add or remove persistent blacklist entries
- `examples/columns.default.json`: default column order
- `examples/batch-config.sample.json`: sample batch configuration for multiple date ranges
- `examples/blacklist.sample.json`: sample blacklist for merge-time filtering
- `examples/blacklist.persistent.json`: persistent blacklist file for ongoing use
- `examples/site-presets.sample.json`: sample custom site preset file for non-default Shopee sites
- `examples/run-config.strict.json`: strict Mall filtering preset
- `examples/run-config.loose.json`: loose Mall filtering preset
- `examples/run-config.custom-safe.json`: recommended configurable Mall filtering preset
- `examples/run-config.beauty.sample.json`: non-`Otomotif` sample showing category override
- `examples/products.sample.json`: sample row payload
- `references/prompt-templates.md`: ready-to-use native AI skill prompt templates
- `references/mall-filter-presets.md`: guidance for choosing Mall filtering behavior

## When To Stop And Ask

Stop and ask the user if:

- the site introduces captchas or MFA
- the Excel columns are not defined
- the required page elements are not discoverable after login
- the marketplace naming differs from the user's rule text
