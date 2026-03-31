# Browser Assisted Login

Real-browser login skill for flows that are partly automatable and partly human-gated.

This skill is built for agent runtimes such as Claude Code, Codex, and OpenClaw. It handles:

- opening a login page in a real browser
- switching login mode when needed
- filling username/password
- submitting the login form
- pausing cleanly for captcha / OTP / QR verification
- resuming after the user finishes the manual step
- reusing browser session state on later runs
- starting from imported browser auth state when direct login is blocked

## Included Files

- `SKILL.md`: trigger conditions and workflow rules
- `agents/openai.yaml`: UI metadata
- `examples/sites.sample.json`: example site configs
- `references/site-config.md`: config schema and guidance
- `references/runbook.md`: ready-to-run operator flow
- `references/auth-state.md`: import existing browser auth state
- `scripts/match_site.py`: match URL to site config
- `scripts/login_state.py`: durable handoff state machine
- `scripts/run_login.py`: executable browser login runner

## Supported Example Sites

- `shopee.menglar.com`
- `shopee.co.id`

These are example presets, not the limit of the skill. Add more site configs in `examples/sites.sample.json` or split them into your own config files.

## Quick Start

Start a login flow:

```bash
python3 browser-assisted-login/scripts/run_login.py start \
  --config browser-assisted-login/examples/sites.sample.json \
  --url "https://example.com/login" \
  --username "<username>" \
  --password "<password>" \
  --state-file /tmp/browser-login-state.json \
  --browser-state-path /tmp/example-auth.json \
  --session-name login-example \
  --headed
```

If the result says `handoff_required`, let the user finish the browser verification step, then resume:

```bash
python3 browser-assisted-login/scripts/run_login.py resume \
  --config browser-assisted-login/examples/sites.sample.json \
  --url "https://example.com/login" \
  --state-file /tmp/browser-login-state.json \
  --session-name login-example \
  --headed
```

## Result States

- `authenticated`: login completed successfully
- `handoff_required`: user must finish captcha / OTP / QR / other verification
- `failed`: no success signal was found; inspect selectors or blockers

## Notes

- Reuse the same `--session-name` for the same site to preserve login state.
- Use a fresh `--session-name` when testing a brand-new login flow.
- Keep credentials out of repo files.
- Keep state files in `/tmp` unless you explicitly want persistence elsewhere.
- Keep imported auth files out of git and treat them like secrets.

## Related Docs

- `references/runbook.md`
- `references/site-config.md`
- `references/auth-state.md`
