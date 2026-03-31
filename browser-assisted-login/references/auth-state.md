# Auth State

Use this path when the site login flow is blocked by anti-bot controls, broken captcha pages, device checks, or similar issues, but the user can already access the site in a normal browser.

## Recommended Approach

1. Export auth state from a real browser session.
2. Start the skill runner with that state file.
3. Let the runner verify whether the imported state already lands in an authenticated page.

## Export From a Running Browser

If the user is already logged in inside Chrome or a Chromium-based browser:

```bash
agent-browser --auto-connect state save /tmp/site-auth.json
```

Then start the runner with:

```bash
python3 browser-assisted-login/scripts/run_login.py start \
  --config browser-assisted-login/examples/sites.sample.json \
  --url "https://example.com/login" \
  --username "<username>" \
  --password "<password>" \
  --state-file /tmp/site-login-state.json \
  --browser-state-path /tmp/site-auth.json \
  --session-name login-example \
  --headed
```

## When To Use This

Prefer imported auth state when:

- captcha pages fail to load
- the site escalates to device trust checks
- the user can log in manually in a normal browser, but automation cannot complete the challenge
- you want to validate post-login flows without fighting the login wall again

## Notes

- Treat auth state files like secrets.
- Do not commit them.
- Keep them in `/tmp` or another local-only path unless the user explicitly wants persistence.
