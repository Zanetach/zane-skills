# zane-skills

Local AI skills repository.

This repo stores reusable native skills for Codex and Claude Code. Each skill lives in its own top-level folder named after the skill.

## Quick Start

Current recommended skill:

- `shopee-id-youying-selector`
- Skill docs: [`shopee-id-youying-selector/SKILL.md`](./shopee-id-youying-selector/SKILL.md)

Quick use:

```text
Use $shopee-id-youying-selector.
友鹰账号：<账号>
友鹰密码：<密码>
站点：菲律宾
时间范围：2025-09-28 到 2026-03-27
按件数降序，筛选 Shopee 站点 Otomotif 类目前10个产品，排除 Shopee Mall 和评分低于 4.7 的商品，导出 Excel。
```

## Skills

| Skill | Purpose |
| --- | --- |
| `shopee-id-youying-selector` | Automate product selection on YouYing Data for Shopee sites and export results to Excel. Default site: Indonesia. |

## Repository Structure

Each skill folder should contain:

- `SKILL.md`: the main skill instructions
- `agents/openai.yaml`: native skill metadata when needed
- `scripts/`: local automation scripts
- `examples/`: sample configs and templates only
- `references/`: prompt templates or supporting docs

Do not commit:

- real credentials
- browser state or cookies
- scraped business data unless intentionally publishing samples

## Install A Skill

For Codex:

```bash
ln -s /path/to/zane-skills/shopee-id-youying-selector ~/.codex/skills/shopee-id-youying-selector
```

For Claude Code:

```bash
ln -s /path/to/zane-skills/shopee-id-youying-selector ~/.agents/skills/shopee-id-youying-selector
```

Or copy the folder directly instead of using a symlink.

## Current Skill

See:

- [`shopee-id-youying-selector/SKILL.md`](./shopee-id-youying-selector/SKILL.md)
