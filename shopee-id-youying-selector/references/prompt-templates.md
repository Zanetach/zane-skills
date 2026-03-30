# Prompt Templates

## Chinese

### Single Range

```text
Use $shopee-id-youying-selector.
登录友鹰，跑 Shopee 指定站点的类目选品。默认示例是印度尼西亚站点的 Otomotif 类目。
站点：菲律宾
类目：Beauty
时间范围：2025-09-28 到 2026-03-27。
固定条件：月销 >= 50，价格 >= 80000 IDR，评分 >= 4.7，排除 Shopee Mall，按件数降序，导出前 10 个到 Excel。
输出到 /Users/zane/Documents/Coderepo/skills/shopee-id-youying-selector/examples/result.xlsx
```

### Multi-Site Single Range

```text
Use $shopee-id-youying-selector.
友鹰账号：<账号>
友鹰密码：<密码>
站点：菲律宾
类目：Beauty
时间范围：2025-09-28 到 2026-03-27
按件数降序，筛选前 10 个产品，排除 Shopee Mall 和评分低于 4.7 的商品，导出 Excel。
```

### Batch Ranges

```text
Use $shopee-id-youying-selector.
按批量日期任务运行 Shopee 指定站点选品。默认示例是印度尼西亚 Otomotif。
日期范围有：
1. 2025-09-28 到 2026-03-27
2. 2025-10-01 到 2026-03-01
固定条件：月销 >= 50，价格 >= 80000 IDR，评分 >= 4.7，排除 Shopee Mall，按件数降序，导出前 10 个。
最后把所有批次结果合并成一个总 Excel。
```

### Merge With Blacklist

```text
Use $shopee-id-youying-selector.
把 batch-output 目录里的批量结果合并成一个总 Excel。
按 product_link 去重，并应用 blacklist.persistent.json。
输出过滤后总表和排除明细。
```

## English

### Single Range

```text
Use $shopee-id-youying-selector to log into YouYing and run Shopee site product selection. Default example: Indonesia Otomotif.
Site: Philippines
Category: Beauty
Date range: 2025-09-28 to 2026-03-27.
Rules: monthly sales >= 50, price >= 80000 IDR, rating >= 4.7, exclude Shopee Mall, sort by sold count descending, export the top 10 rows to Excel.
```

### Multi-Site Single Range

```text
Use $shopee-id-youying-selector.
YouYing username: <username>
YouYing password: <password>
Site: Philippines
Category: Beauty
Date range: 2025-09-28 to 2026-03-27
Sort by sold count descending, exclude Shopee Mall and products with rating below 4.7, then export the top 10 rows to Excel.
```
