#!/opt/homebrew/bin/python3
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


VALID_PHASES = {
    "init",
    "browser_opened",
    "credentials_filled",
    "submitted",
    "handoff_required",
    "resume_requested",
    "authenticated",
    "failed",
}

TRANSITIONS = {
    ("init", "browser_opened"): "browser_opened",
    ("browser_opened", "login_success"): "authenticated",
    ("browser_opened", "login_failed"): "failed",
    ("browser_opened", "credentials_filled"): "credentials_filled",
    ("credentials_filled", "submitted"): "submitted",
    ("submitted", "submit_blocked"): "handoff_required",
    ("submitted", "login_success"): "authenticated",
    ("submitted", "login_failed"): "failed",
    ("handoff_required", "user_done"): "resume_requested",
    ("resume_requested", "resume_success"): "authenticated",
    ("resume_requested", "resume_failed"): "failed",
    ("resume_requested", "still_blocked"): "handoff_required",
    ("failed", "resume_success"): "authenticated",
    ("failed", "resume_failed"): "failed",
    ("failed", "still_blocked"): "handoff_required",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_state(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def cmd_init(args: argparse.Namespace) -> int:
    state = {
        "site": args.site,
        "login_url": args.login_url,
        "phase": "init",
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "last_detail": None,
        "history": [
            {
                "event": "init",
                "phase": "init",
                "detail": None,
                "ts": now_iso(),
            }
        ],
    }
    write_state(Path(args.state_file), state)
    print(json.dumps(state, ensure_ascii=False, indent=2))
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    state = read_state(Path(args.state_file))
    print(json.dumps(state, ensure_ascii=False, indent=2))
    return 0


def cmd_transition(args: argparse.Namespace) -> int:
    path = Path(args.state_file)
    state = read_state(path)
    phase = state.get("phase")
    event = args.event

    if phase not in VALID_PHASES:
        raise SystemExit(f"invalid phase in state file: {phase}")

    next_phase = TRANSITIONS.get((phase, event))
    if next_phase is None:
        print(
            json.dumps(
                {
                    "ok": False,
                    "reason": "invalid_transition",
                    "phase": phase,
                    "event": event,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 2

    record = {
        "event": event,
        "from_phase": phase,
        "phase": next_phase,
        "detail": args.detail,
        "ts": now_iso(),
    }
    state["phase"] = next_phase
    state["updated_at"] = now_iso()
    state["last_detail"] = args.detail
    state.setdefault("history", []).append(record)
    write_state(path, state)
    print(json.dumps(state, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Durable state machine for browser-assisted login flows."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    init_p = sub.add_parser("init", help="Initialize a login state file")
    init_p.add_argument("--state-file", required=True)
    init_p.add_argument("--site", required=True)
    init_p.add_argument("--login-url", required=True)
    init_p.set_defaults(func=cmd_init)

    show_p = sub.add_parser("show", help="Show current state")
    show_p.add_argument("--state-file", required=True)
    show_p.set_defaults(func=cmd_show)

    trans_p = sub.add_parser("transition", help="Apply an event transition")
    trans_p.add_argument("--state-file", required=True)
    trans_p.add_argument("--event", required=True)
    trans_p.add_argument("--detail")
    trans_p.set_defaults(func=cmd_transition)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
