# Site Config

Use site configs to keep the skill generic while handling domain-specific login quirks.

## Required Fields

```json
{
  "id": "site_key",
  "session_name": "login-site-key",
  "match": ["example.com"],
  "login_url": "https://example.com/login",
  "selectors": {
    "username": ["input[name='username']"],
    "password": ["input[type='password']"],
    "submit": ["button[type='submit']"],
    "mode_switch": ["text=Password Login"]
  },
  "success_checks": [
    { "url_not_contains": "/login" },
    { "text_exists": "Dashboard" }
  ],
  "blocker_checks": [
    { "text_exists": "验证码" },
    { "text_exists": "Verification code" },
    { "text_exists": "Scan QR" }
  ],
  "post_login_hints": {
    "landing_text": ["Dashboard", "Workbench"]
  }
}
```

## Notes

- `match`: domain fragments or exact hostnames
- `session_name`: optional persisted browser session key; if omitted, derive from `id`
- `selectors.mode_switch`: optional; use when the site defaults to QR, SMS, or another mode
- `success_checks`: require at least one strong signal before declaring success
- `blocker_checks`: anything that should trigger human handoff
- `post_login_hints`: optional navigation hints after login

## Authoring Guidance

- Keep selectors ordered from most stable to least stable.
- Prefer semantic selectors over CSS chains.
- Include both Chinese and English blocker text when the site is multilingual.
- If login success keeps the same URL, rely on authenticated navigation text instead.
- For high-friction sites, add more than one success check.

## Handoff Policy

When any blocker check matches:

1. stop automated clicks
2. tell the user the single next action
3. wait for `done` or `好了`
4. re-run success checks

Do not loop indefinitely. After two failed resume attempts, explain the blocker clearly.
