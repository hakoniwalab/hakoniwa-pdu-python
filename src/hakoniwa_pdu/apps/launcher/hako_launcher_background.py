from __future__ import annotations

import json
import os
import secrets
import socket
import socketserver
import tempfile
from pathlib import Path
from typing import Any, Protocol

SESSION_VERSION = 1
DEFAULT_CONTROL_HOST = "127.0.0.1"
_TERMINAL_STATES = {"TERMINATED", "FAILED"}
_MAX_REQUEST_BYTES = 64 * 1024


class LauncherLifecycle(Protocol):
    def terminate(self) -> None: ...
    def status(self) -> str: ...


class LauncherControlError(RuntimeError):
    pass


def _path(value: str | os.PathLike[str]) -> Path:
    return Path(value).expanduser().resolve()


def read_session(path: str | os.PathLike[str]) -> dict[str, Any]:
    session_path = _path(path)
    try:
        data = json.loads(session_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise LauncherControlError(f"session file not found: {session_path}") from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise LauncherControlError(f"cannot read session file {session_path}: {exc}") from exc
    if not isinstance(data, dict):
        raise LauncherControlError(f"invalid session file: {session_path}")
    return data


def write_session(path: str | os.PathLike[str], payload: dict[str, Any]) -> Path:
    session_path = _path(path)
    session_path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        prefix=f".{session_path.name}.",
        suffix=".tmp",
        dir=session_path.parent,
        text=True,
    )
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.chmod(tmp_path, 0o600)
        except OSError:
            pass
        os.replace(tmp_path, session_path)
    finally:
        try:
            tmp_path.unlink(missing_ok=True)
        except OSError:
            pass
    return session_path


def is_terminal_session(data: dict[str, Any]) -> bool:
    return str(data.get("state", "")).upper() in _TERMINAL_STATES


class _ControlHandler(socketserver.StreamRequestHandler):
    def handle(self) -> None:
        server = self.server
        if not isinstance(server, LauncherControlServer):
            return
        raw = self.rfile.readline(_MAX_REQUEST_BYTES)
        if not raw:
            return
        try:
            request = json.loads(raw.decode("utf-8"))
            response = server.dispatch(request)
        except Exception as exc:
            response = {"ok": False, "error": str(exc), "pid": os.getpid()}
        self.wfile.write((json.dumps(response) + "\n").encode("utf-8"))
        self.wfile.flush()


class LauncherControlServer(socketserver.TCPServer):
    allow_reuse_address = True

    def __init__(
        self,
        *,
        service: LauncherLifecycle,
        session_path: str | os.PathLike[str],
        launch_file: str | os.PathLike[str],
        log_file: str | os.PathLike[str],
        token: str | None = None,
    ) -> None:
        super().__init__((DEFAULT_CONTROL_HOST, 0), _ControlHandler)
        self.service = service
        self.session_path = _path(session_path)
        self.launch_file = _path(launch_file)
        self.log_file = _path(log_file)
        self.token = token or secrets.token_urlsafe(32)
        self.stop_requested = False
        self._last_persisted_state: str | None = None

    @property
    def control_host(self) -> str:
        return str(self.server_address[0])

    @property
    def control_port(self) -> int:
        return int(self.server_address[1])

    def session_payload(self) -> dict[str, Any]:
        return {
            "version": SESSION_VERSION,
            "pid": os.getpid(),
            "control_host": self.control_host,
            "control_port": self.control_port,
            "token": self.token,
            "launch_file": str(self.launch_file),
            "log_file": str(self.log_file),
            "state": self.service.status(),
        }

    def persist(self, *, force: bool = False) -> None:
        state = self.service.status()
        if force or state != self._last_persisted_state:
            write_session(self.session_path, self.session_payload())
            self._last_persisted_state = state

    def dispatch(self, request: Any) -> dict[str, Any]:
        if not isinstance(request, dict):
            return {"ok": False, "error": "request must be a JSON object", "pid": os.getpid()}
        if request.get("token") != self.token:
            return {"ok": False, "error": "unauthorized session token", "pid": os.getpid()}
        expected_pid = request.get("pid")
        if expected_pid is not None and int(expected_pid) != os.getpid():
            return {"ok": False, "error": "session pid mismatch", "pid": os.getpid()}

        command = str(request.get("command", ""))
        if command == "status":
            self.persist()
            return {"ok": True, "pid": os.getpid(), "state": self.service.status()}
        if command == "terminate":
            self.service.terminate()
            self.stop_requested = True
            self.persist(force=True)
            return {"ok": True, "pid": os.getpid(), "state": self.service.status()}
        return {"ok": False, "error": f"unknown command: {command}", "pid": os.getpid()}

    def serve_until_terminated(self, poll_interval: float = 0.2) -> None:
        self.timeout = poll_interval
        self.persist(force=True)
        try:
            while not self.stop_requested and self.service.status() != "TERMINATED":
                self.handle_request()
                self.persist()
        finally:
            self.persist(force=True)


def send_control_command(
    session_file: str | os.PathLike[str],
    command: str,
    *,
    timeout_sec: float = 3.0,
) -> dict[str, Any]:
    session = read_session(session_file)
    try:
        host = str(session["control_host"])
        port = int(session["control_port"])
        token = str(session["token"])
        pid = int(session["pid"])
    except (KeyError, TypeError, ValueError) as exc:
        raise LauncherControlError("session file does not contain a usable control endpoint") from exc

    request = {"command": command, "token": token, "pid": pid}
    try:
        with socket.create_connection((host, port), timeout=timeout_sec) as sock:
            sock.settimeout(timeout_sec)
            stream = sock.makefile("rwb")
            stream.write((json.dumps(request) + "\n").encode("utf-8"))
            stream.flush()
            raw = stream.readline(_MAX_REQUEST_BYTES)
    except OSError as exc:
        raise LauncherControlError(f"cannot reach launcher control endpoint: {exc}") from exc

    if not raw:
        raise LauncherControlError("launcher control endpoint closed without a response")
    try:
        response = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise LauncherControlError("launcher control endpoint returned invalid JSON") from exc
    if not isinstance(response, dict):
        raise LauncherControlError("launcher control endpoint returned an invalid response")
    if int(response.get("pid", -1)) != pid:
        raise LauncherControlError("launcher response pid does not match session ownership")
    if response.get("ok") is not True:
        raise LauncherControlError(str(response.get("error", "launcher command failed")))
    return response
