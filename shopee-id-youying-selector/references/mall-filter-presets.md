# Mall Filter Presets

## 1. strict

Use when you only want to exclude results that look explicitly like `Shopee Mall`.

Recommended config:

```json
{
  "mall_filter_mode": "strict",
  "mall_keywords": [],
  "mall_exclude_keywords": []
}
```

## 2. loose

Use when you want to exclude anything that looks like `Mall`, `Official`, or `Official Shop`.

Recommended config:

```json
{
  "mall_filter_mode": "loose",
  "mall_keywords": [
    "mall",
    "official",
    "official shop"
  ],
  "mall_exclude_keywords": []
}
```

## 3. custom-safe

Use when you want a configurable default that is easier to tune later. This is the recommended preset for ongoing operations.

Recommended config:

```json
{
  "mall_filter_mode": "custom",
  "mall_keywords": [
    "mall",
    "official",
    "official shop"
  ],
  "mall_exclude_keywords": []
}
```

## Recommendation

Default to `custom-safe` unless the business team has explicitly decided otherwise.

- choose `strict` if false positives are unacceptable
- choose `loose` if avoiding official-store inventory matters more than recall
- choose `custom-safe` if the rule will evolve over time
