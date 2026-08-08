from __future__ import annotations

import errno
import json
import os
import secrets
import socket
import socketserver
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, Protocol

SESSION_VERSION = 1
DEFAULT_CONTROL_HOST = "127.0.0.1"
_TERMINAL_STATES = {"TERMINATED", "FAILED"}
_MAX_REQUEST_BYTES = 64 * 1024
_SESSION_PERSIST_LOCK_TIMEOUT_SEC = 1.0
_SESSION_LOCK_RETRY_INTERVAL_SEC = 0.01


class LauncherLifecycle(Protocol):
    def terminate(self) -> None: ...
    def status(self) -> str: ...


class LauncherControlError(RuntimeError):
    pass


class LauncherSessionConflict(LauncherControlError):
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


def reserve_session(path: str | os.PathLike[str], payload: dict[str, Any]) -> Path:
    """Atomically create the initial session without overwriting another launcher."""
    session_path = _path(path)
    session_path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        prefix=f".{session_path.name}.",
        suffix=".reserve",
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
        # A same-directory hard link publishes the complete file atomically and
        # fails rather than replacing an existing session.
        os.link(tmp_path, session_path)
    finally:
        tmp_path.unlink(missing_ok=True)
    return session_path


def write_owned_session(
    path: str | os.PathLike[str],
    payload: dict[str, Any],
    *,
    session_id: str,
    lock_timeout_sec: float = 0.0,
) -> Path:
    """Atomically update a session only while this launcher still owns it."""
    with session_file_lock(path, timeout_sec=lock_timeout_sec):
        current = read_session(path)
        if current.get("session_id") != session_id:
            raise LauncherControlError("session ownership changed")
        return write_session(path, payload)


def new_session_id() -> str:
    return secrets.token_urlsafe(32)


@contextmanager
def session_file_lock(
    path: str | os.PathLike[str],
    *,
    timeout_sec: float = 0.0,
) -> Iterator[None]:
    """Serialize session inspection and reservation across processes.

    The default remains fail-fast for competing launch reservations. Existing
    session owners may opt into a bounded wait while persisting state.
    """
    session_path = _path(path)
    lock_path = session_path.with_name(f".{session_path.name}.lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + max(0.0, timeout_sec)
    with lock_path.open("a+b") as lock_stream:
        try:
            os.chmod(lock_path, 0o600)
        except OSError:
            pass
        lock_stream.seek(0, os.SEEK_END)
        if lock_stream.tell() == 0:
            lock_stream.write(b"\0")
            lock_stream.flush()

        while True:
            lock_stream.seek(0)
            try:
                if os.name == "nt":
                    import msvcrt

                    msvcrt.locking(lock_stream.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl

                    fcntl.flock(
                        lock_stream.fileno(),
                        fcntl.LOCK_EX | fcntl.LOCK_NB,
                    )
            except OSError as exc:
                remaining = deadline - time.monotonic()
                if (
                    exc.errno not in (errno.EACCES, errno.EAGAIN)
                    or remaining <= 0
                ):
                    raise LauncherControlError(
                        f"another launcher is preparing session file: {session_path}"
                    ) from exc
                time.sleep(min(_SESSION_LOCK_RETRY_INTERVAL_SEC, remaining))
            else:
                break

        try:
            yield
        finally:
            lock_stream.seek(0)
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(lock_stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(lock_stream.fileno(), fcntl.LOCK_UN)


def is_process_alive(pid: int) -> bool:
    """Probe process liveness without sending a terminating signal."""
    if pid <= 0:
        return False
    if pid == os.getpid():
        return True
    if os.name == "nt":
        import ctypes

        process_query_limited_information = 0x1000
        handle = ctypes.windll.kernel32.OpenProcess(
            process_query_limited_information,
            False,
            pid,
        )
        if handle:
            ctypes.windll.kernel32.CloseHandle(handle)
            return True
        # Access denied is conservative evidence that the process exists.
        return ctypes.windll.kernel32.GetLastError() == 5
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError as exc:
        return exc.errno == errno.EPERM
    return True


def is_terminal_session(data: dict[str, Any]) -> bool:
    return str(data.get("state", "")).upper() in _TERMINAL_STATES


def _read_session_for_claim(session_path: Path) -> dict[str, Any]:
    try:
        return read_session(session_path)
    except LauncherControlError as exc:
        raise LauncherSessionConflict(
            f"refusing to overwrite unreadable session file "
            f"{session_path}: {exc}"
        ) from exc


def claim_session(
    path: str | os.PathLike[str],
    payload: dict[str, Any],
    *,
    status_timeout_sec: float = 1.0,
) -> Path:
    """Validate any prior owner and atomically reserve a session for a new run."""
    session_path = _path(path)
    with session_file_lock(session_path):
        if not session_path.exists():
            return reserve_session(session_path, payload)

        existing = _read_session_for_claim(session_path)
        if is_terminal_session(existing):
            session_path.unlink(missing_ok=True)
            return reserve_session(session_path, payload)
        observed_session_id = existing.get("session_id")

    # A live owner may need the same lock while servicing status or persisting a
    # startup transition. Do not hold the reservation lock across network I/O.
    try:
        response = send_control_command(
            session_path,
            "status",
            timeout_sec=status_timeout_sec,
        )
        probe_error: LauncherControlError | None = None
    except LauncherControlError as exc:
        response = None
        probe_error = exc

    with session_file_lock(session_path):
        if not session_path.exists():
            return reserve_session(session_path, payload)

        current = _read_session_for_claim(session_path)
        if current.get("session_id") != observed_session_id:
            raise LauncherSessionConflict(
                f"background session changed while validating: {session_path}"
            )
        if is_terminal_session(current):
            session_path.unlink(missing_ok=True)
            return reserve_session(session_path, payload)

        if response is not None:
            raise LauncherSessionConflict(
                f"background session is already active: "
                f"{session_path} (state={response.get('state')})"
            )

        assert probe_error is not None
        try:
            pid = int(current["pid"])
        except (KeyError, TypeError, ValueError) as pid_exc:
            raise LauncherSessionConflict(
                f"refusing to replace an unreachable session without "
                f"a usable owner PID: {session_path}: {probe_error}"
            ) from pid_exc
        if is_process_alive(pid):
            raise LauncherSessionConflict(
                f"refusing to replace an unreachable session whose "
                f"recorded process may still be alive: {session_path}: {probe_error}"
            ) from probe_error

        session_path.unlink(missing_ok=True)
        return reserve_session(session_path, payload)


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
        session_id: str,
        token: str | None = None,
    ) -> None:
        super().__init__((DEFAULT_CONTROL_HOST, 0), _ControlHandler)
        self.service = service
        self.session_path = _path(session_path)
        self.launch_file = _path(launch_file)
        self.log_file = _path(log_file)
        self.session_id = session_id
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
            "session_id": self.session_id,
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
            write_owned_session(
                self.session_path,
                self.session_payload(),
                session_id=self.session_id,
                lock_timeout_sec=_SESSION_PERSIST_LOCK_TIMEOUT_SEC,
            )
            self._last_persisted_state = state

    def dispatch(self, request: Any) -> dict[str, Any]:
        if not isinstance(request, dict):
            return {"ok": False, "error": "request must be a JSON object", "pid": os.getpid()}
        if request.get("token") != self.token:
            return {"ok": False, "error": "unauthorized session token", "pid": os.getpid()}
        if request.get("session_id") != self.session_id:
            return {"ok": False, "error": "session ownership mismatch", "pid": os.getpid()}
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
        session_id = str(session["session_id"])
    except (KeyError, TypeError, ValueError) as exc:
        raise LauncherControlError("session file does not contain a usable control endpoint") from exc

    if host != DEFAULT_CONTROL_HOST:
        raise LauncherControlError("launcher control endpoint is not localhost")

    request = {
        "command": command,
        "token": token,
        "pid": pid,
        "session_id": session_id,
    }
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
