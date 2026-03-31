# Runbook

Use this runbook when you want to operate the skill quickly without rethinking the flow.

## Standard Operator Flow

1. Match the site config.
2. Start the login run.
3. Inspect the result JSON.
4. If `status=handoff_required`, ask the user to finish verification in the browser.
5. After the user replies `好了` or `done`, run `resume`.
6. If `status=authenticated`, continue to the user's real task.

## Menglar Example

Start:

```bash
python3 skills/browser-assisted-login/scripts/run_login.py start \
  --config skills/browser-assisted-login/examples/sites.sample.json \
  --url "https://shopee.menglar.com/workbench/login?urlCode=1637911731749" \
  --username "<username>" \
  --password "<password>" \
  --state-file /tmp/menglar-login-state.json \
  --session-name login-menglar-shopee \
  --headed
```

Resume:

```bash
python3 skills/browser-assisted-login/scripts/run_login.py resume \
  --config skills/browser-assisted-login/examples/sites.sample.json \
  --url "https://shopee.menglar.com/workbench/login?urlCode=1637911731749" \
  --state-file /tmp/menglar-login-state.json \
  --session-name login-menglar-shopee \
  --headed
```

## Shopee Indonesia Example

Start:

```bash
python3 skills/browser-assisted-login/scripts/run_login.py start \
  --config skills/browser-assisted-login/examples/sites.sample.json \
  --url "https://shopee.co.id/buyer/login" \
  --username "<username>" \
  --password "<password>" \
  --state-file /tmp/shopee-id-login-state.json \
  --session-name login-shopee-co-id \
  --headed
```

Resume:

```bash
python3 skills/browser-assisted-login/scripts/run_login.py resume \
  --config skills/browser-assisted-login/examples/sites.sample.json \
  --url "https://shopee.co.id/buyer/login" \
  --state-file /tmp/shopee-id-login-state.json \
  --session-name login-shopee-co-id \
  --headed
```

## Result Handling

If start or resume returns:

- `authenticated`
  - continue to the real user task
- `handoff_required`
  - ask the user to complete the verification in the browser
- `failed`
  - inspect the page, tighten selectors or blockers, and rerun

## Short User Messages

Prefer these messages:

- `正在打开登录页。`
- `正在填写账号密码。`
- `现在请在浏览器里手动完成验证，完成后回复“好了”。`
- `已检测到登录成功。`

## Notes

- Reuse the same `--session-name` for the same site to keep login state.
- Use a new `--session-name` when you want a fresh login test.
- Keep state files in `/tmp` unless the user asks for a persistent location.
