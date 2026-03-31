#!/opt/homebrew/bin/python3
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


def run(cmd: list[str], check: bool = True) -> str:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if check and proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or "command failed")
    return proc.stdout.strip()


def runner_prefix(
    headed: bool,
    session_name: str | None = None,
    browser_state_path: str | None = None,
) -> list[str]:
    prefix = ["agent-browser"]
    if headed:
        prefix.append("--headed")
    if session_name:
        prefix.extend(["--session-name", session_name])
    if browser_state_path:
        prefix.extend(["--state", browser_state_path])
    return prefix


def match_site(config_path: str, url: str) -> dict[str, Any]:
    script = Path(__file__).with_name("match_site.py")
    out = run(
        [
            sys.executable,
            str(script),
            "--config",
            config_path,
            "--url",
            url,
        ]
    )
    data = json.loads(out)
    if not data.get("matched"):
        raise RuntimeError(f"no site config matched for {url}")
    return data["site"]


def js_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def query_expression(selector: str) -> str:
    if selector.startswith("text="):
        needle = selector[len("text=") :].strip()
        return f"""
Array.from(document.querySelectorAll("*")).find(el => {{
  const text = (el.innerText || el.textContent || "").trim();
  return text === {js_string(needle)} || text.includes({js_string(needle)});
}})
"""
    return f"document.querySelector({js_string(selector)})"


def session_name_for_site(site: dict[str, Any]) -> str:
    configured = site.get("session_name")
    if isinstance(configured, str) and configured.strip():
        return configured.strip()
    site_id = str(site["id"])
    normalized = re.sub(r"[^a-zA-Z0-9._-]+", "-", site_id).strip("-").lower()
    return f"login-{normalized}"


def eval_js(
    js: str,
    headed: bool,
    session_name: str | None = None,
    browser_state_path: str | None = None,
) -> str:
    return run(runner_prefix(headed, session_name, browser_state_path) + ["eval", js])


def eval_json(
    js: str,
    headed: bool,
    session_name: str | None = None,
    browser_state_path: str | None = None,
) -> Any:
    raw = eval_js(js, headed, session_name, browser_state_path)
    data = json.loads(raw)
    if isinstance(data, str):
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return data
    return data


def open_url(
    url: str,
    headed: bool,
    session_name: str | None = None,
    browser_state_path: str | None = None,
) -> None:
    run(runner_prefix(headed, session_name, browser_state_path) + ["open", url])
    run(
        runner_prefix(headed, session_name, browser_state_path)
        + ["wait", "--load", "networkidle"]
    )


def click_first(
    selectors: list[str],
    headed: bool,
    session_name: str | None = None,
    browser_state_path: str | None = None,
) -> bool:
    for selector in selectors:
        js = f"""
(() => {{
  const el = {query_expression(selector)};
  if (!el) return JSON.stringify({{"ok": false}});
  el.click();
  return JSON.stringify({{"ok": true, "selector": {js_string(selector)}}});
}})()
"""
        data = eval_json(js, headed, session_name, browser_state_path)
        if data.get("ok"):
            return True
    return False


def fill_first(
    selectors: list[str],
    value: str,
    headed: bool,
    session_name: str | None = None,
    browser_state_path: str | None = None,
) -> str | None:
    for selector in selectors:
        js = f"""
(() => {{
  const el = {query_expression(selector)};
  if (!el) return JSON.stringify({{"ok": false}});
  el.focus();
  el.value = {js_string(value)};
  el.dispatchEvent(new Event("input", {{ bubbles: true }}));
  el.dispatchEvent(new Event("change", {{ bubbles: true }}));
  return JSON.stringify({{"ok": true, "selector": {js_string(selector)}}});
}})()
"""
        data = eval_json(js, headed, session_name, browser_state_path)
        if data.get("ok"):
            return data["selector"]
    return None


def get_url(
    headed: bool,
    session_name: str | None = None,
    browser_state_path: str | None = None,
) -> str:
    return run(runner_prefix(headed, session_name, browser_state_path) + ["get", "url"])


def check_text_exists(
    text: str,
    headed: bool,
    session_name: str | None = None,
    browser_state_path: str | None = None,
) -> bool:
    js = f"document.body && document.body.innerText.includes({js_string(text)})"
    return eval_js(js, headed, session_name, browser_state_path).strip().lower() == "true"


def check_selector_exists(
    selector: str,
    headed: bool,
    session_name: str | None = None,
    browser_state_path: str | None = None,
) -> bool:
    js = f"Boolean({query_expression(selector)})"
    return eval_js(js, headed, session_name, browser_state_path).strip().lower() == "true"


def is_authenticated(
    site: dict[str, Any],
    headed: bool,
    session_name: str | None = None,
    browser_state_path: str | None = None,
) -> bool:
    current_url = get_url(headed, session_name, browser_state_path)
    for check in site.get("success_checks", []):
        if "url_not_contains" in check and check["url_not_contains"] not in current_url:
            return True
        if "text_exists" in check and check_text_exists(
            check["text_exists"], headed, session_name, browser_state_path
        ):
            return True
        if "selector_exists" in check and check_selector_exists(
            check["selector_exists"], headed, session_name, browser_state_path
        ):
            return True
    return False


def is_blocked(
    site: dict[str, Any],
    headed: bool,
    session_name: str | None = None,
    browser_state_path: str | None = None,
) -> str | None:
    for check in site.get("blocker_checks", []):
        if "text_exists" in check and check_text_exists(
            check["text_exists"], headed, session_name, browser_state_path
        ):
            return check["text_exists"]
        if "selector_exists" in check and check_selector_exists(
            check["selector_exists"], headed, session_name, browser_state_path
        ):
            return check["selector_exists"]
    return None


def transition_state(state_file: str, event: str, detail: str | None = None) -> None:
    script = Path(__file__).with_name("login_state.py")
    cmd = [
        sys.executable,
        str(script),
        "transition",
        "--state-file",
        state_file,
        "--event",
        event,
    ]
    if detail:
        cmd.extend(["--detail", detail])
    run(cmd)


def init_state(state_file: str, site_id: str, login_url: str) -> None:
    script = Path(__file__).with_name("login_state.py")
    run(
        [
            sys.executable,
            str(script),
            "init",
            "--state-file",
            state_file,
            "--site",
            site_id,
            "--login-url",
            login_url,
        ]
    )


def read_state(state_file: str) -> dict[str, Any]:
    return json.loads(Path(state_file).read_text(encoding="utf-8"))


def short_result(
    status: str,
    site_id: str,
    session_name: str,
    message: str,
    reused_session: bool = False,
    used_browser_state: bool = False,
) -> int:
    print(
        json.dumps(
            {
                "status": status,
                "site": site_id,
                "session_name": session_name,
                "reused_session": reused_session,
                "used_browser_state": used_browser_state,
                "message": message,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if status != "failed" else 1


def start_flow(args: argparse.Namespace) -> int:
    site = match_site(args.config, args.url)
    selectors = site.get("selectors", {})
    session_name = args.session_name or session_name_for_site(site)
    browser_state_path = args.browser_state_path

    init_state(args.state_file, site["id"], site["login_url"])
    open_url(site["login_url"], args.headed, session_name, browser_state_path)
    transition_state(args.state_file, "browser_opened")

    if is_authenticated(site, args.headed, session_name, browser_state_path):
        transition_state(args.state_file, "login_success")
        return short_result(
            "authenticated",
            site["id"],
            session_name,
            "Existing authenticated session was reused.",
            reused_session=True,
            used_browser_state=bool(browser_state_path),
        )

    mode_switch = selectors.get("mode_switch", [])
    if mode_switch:
        click_first(mode_switch, args.headed, session_name, browser_state_path)

    username_sel = fill_first(
        selectors.get("username", []),
        args.username,
        args.headed,
        session_name,
        browser_state_path,
    )
    password_sel = fill_first(
        selectors.get("password", []),
        args.password,
        args.headed,
        session_name,
        browser_state_path,
    )
    if not username_sel or not password_sel:
        transition_state(args.state_file, "login_failed", "missing login fields")
        return short_result(
            "failed",
            site["id"],
            session_name,
            "Could not locate username or password field.",
            used_browser_state=bool(browser_state_path),
        )

    transition_state(args.state_file, "credentials_filled")
    if not click_first(
        selectors.get("submit", []), args.headed, session_name, browser_state_path
    ):
        transition_state(args.state_file, "login_failed", "missing submit control")
        return short_result(
            "failed",
            site["id"],
            session_name,
            "Could not locate submit control.",
            used_browser_state=bool(browser_state_path),
        )

    run(runner_prefix(args.headed, session_name, browser_state_path) + ["wait", "1500"])
    transition_state(args.state_file, "submitted")

    if is_authenticated(site, args.headed, session_name, browser_state_path):
        transition_state(args.state_file, "login_success")
        return short_result(
            "authenticated",
            site["id"],
            session_name,
            "Login succeeded.",
            used_browser_state=bool(browser_state_path),
        )

    blocker = is_blocked(site, args.headed, session_name, browser_state_path)
    if blocker:
        transition_state(args.state_file, "submit_blocked", blocker)
        return short_result(
            "handoff_required",
            site["id"],
            session_name,
            f"Manual verification required: {blocker}. Ask the user to finish it in the browser, then run resume.",
            used_browser_state=bool(browser_state_path),
        )

    transition_state(args.state_file, "login_failed", "no success signal after submit")
    return short_result(
        "failed",
        site["id"],
        session_name,
        "Submit completed but no success signal was detected.",
        used_browser_state=bool(browser_state_path),
    )


def resume_flow(args: argparse.Namespace) -> int:
    site = match_site(args.config, args.url)
    session_name = args.session_name or session_name_for_site(site)
    browser_state_path = args.browser_state_path
    state = read_state(args.state_file)
    if state.get("phase") == "handoff_required":
        transition_state(args.state_file, "user_done")

    if is_authenticated(site, args.headed, session_name, browser_state_path):
        transition_state(args.state_file, "resume_success")
        return short_result(
            "authenticated",
            site["id"],
            session_name,
            "Login succeeded after manual verification.",
            used_browser_state=bool(browser_state_path),
        )

    blocker = is_blocked(site, args.headed, session_name, browser_state_path)
    if blocker:
        transition_state(args.state_file, "still_blocked", blocker)
        return short_result(
            "handoff_required",
            site["id"],
            session_name,
            f"Verification is still blocking progress: {blocker}.",
            used_browser_state=bool(browser_state_path),
        )

    transition_state(args.state_file, "resume_failed", "resume check found no success signal")
    return short_result(
        "failed",
        site["id"],
        session_name,
        "Resume check did not find a successful authenticated state.",
        used_browser_state=bool(browser_state_path),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a browser-assisted login flow.")
    sub = parser.add_subparsers(dest="command", required=True)

    start = sub.add_parser("start", help="Start a login flow")
    start.add_argument("--config", required=True)
    start.add_argument("--url", required=True)
    start.add_argument("--username", required=True)
    start.add_argument("--password", required=True)
    start.add_argument("--state-file", required=True)
    start.add_argument("--session-name")
    start.add_argument("--browser-state-path")
    start.add_argument("--headed", action="store_true")
    start.set_defaults(func=start_flow)

    resume = sub.add_parser("resume", help="Resume after manual verification")
    resume.add_argument("--config", required=True)
    resume.add_argument("--url", required=True)
    resume.add_argument("--state-file", required=True)
    resume.add_argument("--session-name")
    resume.add_argument("--browser-state-path")
    resume.add_argument("--headed", action="store_true")
    resume.set_defaults(func=resume_flow)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
