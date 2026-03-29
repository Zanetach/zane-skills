# zane-skills

Local AI skills repository.

This repo stores reusable native skills for Codex and Claude Code. Each skill lives in its own top-level folder named after the skill.

## Skills

| Skill | Purpose |
| --- | --- |
| `shopee-id-youying-selector` | Automate product selection on YouYing Data for Shopee Indonesia and export results to Excel. |

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
