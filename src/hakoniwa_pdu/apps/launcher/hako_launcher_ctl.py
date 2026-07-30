from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .hako_launcher_background import (
    LauncherControlError,
    is_terminal_session,
    read_session,
    send_control_command,
)


def _print(payload: dict) -> None:
    print(json.dumps(payload, ensure_ascii=False))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Hakoniwa Launcher background control")
    parser.add_argument("command", choices=["status", "terminate"])
    parser.add_argument("session_file", type=Path)
    args = parser.parse_args(argv)

    try:
        session = read_session(args.session_file)
    except LauncherControlError as exc:
        print(f"[launcher-ctl] {exc}", file=sys.stderr)
        return 2

    state = str(session.get("state", "UNKNOWN"))
    if is_terminal_session(session):
        _print({"ok": state == "TERMINATED", "state": state, "pid": session.get("pid")})
        return 0 if state == "TERMINATED" else 1

    try:
        response = send_control_command(args.session_file, args.command)
    except LauncherControlError as exc:
        _print({"ok": False, "state": "STALE", "pid": session.get("pid"), "error": str(exc)})
        return 1

    _print(response)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
