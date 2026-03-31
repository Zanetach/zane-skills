---
name: browser-assisted-login
description: Use when the user wants to log into a website in a real browser, especially when the flow may include password entry, login-mode switching, captcha, SMS/email OTP, QR code login, or other human verification steps. Supports a human-in-the-loop handoff: the agent fills and submits what it can, pauses for manual verification, then resumes and saves reusable session state.
---

# Browser Assisted Login

Use this skill for browser-based login flows that are partly automatable and partly human-gated.

This skill is designed for Claude Code, Codex, OpenClaw, and similar agent runtimes that can:

- open a real browser
- inspect and interact with the page
- wait for the user to finish manual verification
- reuse session state after success

## What This Skill Is For

Use this skill when the user says things like:

- "帮我登录这个网站"
- "log into this site"
- "open the login page and sign in"
- "fill my username and password and wait for me to do the captcha"

This skill is the right default for:

- username/password login
- phone/password login
- email/password login
- login flows with captcha or slider verification
- login flows with SMS, email OTP, or QR scan that the user must finish manually

## What This Skill Is Not For

Do not promise full automation for:

- captcha solving by the agent
- OTP retrieval from the user's phone or inbox unless another tool explicitly provides it
- enterprise login flows that require local certificates, hardware keys, or native apps
- sites that actively block automated browsers and require custom evasion work

In those cases, this skill still helps by automating setup and handoff, but not by bypassing the security check.

## Core Workflow

1. Open the target login URL in a visible browser when possible.
2. Detect the login form and switch login mode if needed.
3. Fill credentials provided by the user or reuse existing authenticated state.
4. Submit the form.
5. If the page requests captcha, OTP, QR scan, or another human verification step:
   - stop browser actions
   - tell the user exactly one short thing to do
   - ask the user to reply with `好了`, `done`, or equivalent when finished
6. After the user confirms, re-check page state.
7. If login succeeded, save session/profile/state for reuse.
8. Continue to the user's real goal after login instead of stopping at "login complete".

## User-Facing Behavior

Keep prompts simple. Prefer:

- `正在打开登录页。`
- `正在填写账号密码。`
- `现在请在浏览器里手动完成验证码，完成后回复“好了”。`
- `已检测到登录成功。`

Do not expose implementation details like selectors, iframes, DOM refs, CDP, or cross-origin errors unless debugging is explicitly requested.

## Credential Handling

Preferred order:

1. Reuse existing browser profile or saved session state
2. Let the user log in manually once, then save state
3. Use credentials given in-chat for the current run only

Rules:

- do not write plaintext credentials into repo files
- do not commit cookies, browser profiles, or auth state
- warn briefly if the user shares credentials in chat that conversation history may retain them

## Session Strategy

After a successful login, persist one of:

- browser profile
- named session
- storage state file

Prefer domain-scoped reuse. On future runs:

- load saved state first
- verify whether the session is still valid
- only fall back to manual login if reuse fails

## Site Configuration

Use a site config when the target domain is known. Configs should define:

- domain match rules
- login URL
- candidate selectors for username, password, submit, and mode switch
- success checks
- blocker checks
- post-login landing hints

Read [references/site-config.md](references/site-config.md) before creating or editing configs.
Read [references/runbook.md](references/runbook.md) when you want a ready-to-run operator flow for a real login task.

Use [examples/sites.sample.json](examples/sites.sample.json) as the starter format.

For deterministic config matching and handoff state, use:

- `scripts/match_site.py`
- `scripts/login_state.py`
- `scripts/run_login.py`

## Human-In-The-Loop Rules

When a verification step appears:

- do not keep blindly clicking
- do not claim the agent can solve the challenge unless it actually can
- pause cleanly
- ask for one concrete user action
- resume only after the user confirms completion

Recommended confirmation phrases to accept:

- `好了`
- `done`
- `ok`
- `已完成`

## Success Criteria

Treat login as successful only when at least one success check passes, for example:

- URL no longer matches the login page
- a known post-login navigation element appears
- the login form disappears and authenticated UI appears

If uncertain, say so and verify with another page inspection instead of assuming success.

## Minimal Output Contract

At the end of the login step, report:

- whether login succeeded
- whether session state was reused or freshly established
- whether manual verification was required
- what page or app area is now available

Then continue to the user's actual task.

## Script Helpers

### Match a site config

Use this when the user gives a URL or hostname and you want the best matching site preset:

```bash
python3 scripts/match_site.py \
  --config examples/sites.sample.json \
  --url "https://shopee.co.id/buyer/login"
```

This prints the matching config object as JSON.

### Manage login handoff state

Use this when the browser flow needs a durable state machine:

```bash
python3 scripts/login_state.py init \
  --state-file /tmp/browser-login-state.json \
  --site shopee_co_id \
  --login-url "https://shopee.co.id/buyer/login"

python3 scripts/login_state.py transition \
  --state-file /tmp/browser-login-state.json \
  --event submit_blocked \
  --detail "captcha detected"

python3 scripts/login_state.py transition \
  --state-file /tmp/browser-login-state.json \
  --event user_done
```

State phases:

- `init`
- `browser_opened`
- `credentials_filled`
- `submitted`
- `handoff_required`
- `resume_requested`
- `authenticated`
- `failed`

### Run the login flow

Use this when you want the skill to execute the browser login workflow end to end:

```bash
python3 scripts/run_login.py start \
  --config examples/sites.sample.json \
  --url "https://shopee.co.id/buyer/login" \
  --username "your_username" \
  --password "your_password" \
  --state-file /tmp/browser-login-state.json \
  --headed
```

If the flow pauses for captcha, OTP, or QR verification, ask the user to complete it in the browser and then resume:

```bash
python3 scripts/run_login.py resume \
  --config examples/sites.sample.json \
  --url "https://shopee.co.id/buyer/login" \
  --state-file /tmp/browser-login-state.json \
  --headed
```

The runner returns a JSON object with:

- `status`: `authenticated`, `handoff_required`, or `failed`
- `site`: matched site id
- `session_name`: browser session key used for reuse
- `reused_session`: whether the runner detected an already-authenticated session
- `message`: short human-readable result

By default the runner uses a domain-scoped session name from site config, so future runs on the same site can reuse prior login state.
