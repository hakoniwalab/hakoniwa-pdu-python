from __future__ import annotations
import sys
import os
import argparse
import signal
import threading
import time
import asyncio
import json
import logging
import subprocess
from pathlib import Path
from typing import Optional

from .loader import load
from .hako_monitor import HakoMonitor
from .hako_cli import HakoCli
from .hako_launcher_control import (
    LauncherControlError,
    LauncherControlServer,
    claim_session,
    new_session_id,
    read_session,
    send_control_command,
    write_owned_session,
)

_BACKGROUND_READY_TIMEOUT_SEC = 60.0
_BACKGROUND_SHUTDOWN_TIMEOUT_SEC = 30.0


class LauncherService:
    """起動・監視・停止を状態付きで提供。"""

    def __init__(self, *, launch_path: str) -> None:
        self.launcher_spec, self.spec = load(launch_path)  # (LauncherSpec, EffectiveSpec)
        self.defaults_env_ops = None
        if self.launcher_spec.defaults and self.launcher_spec.defaults.env:
            self.defaults_env_ops = self.launcher_spec.defaults.env.model_dump(exclude_none=True)

        self.monitor = HakoMonitor(self.spec, defaults_env_ops=self.defaults_env_ops)
        self.cli     = HakoCli(spec=self.spec, defaults_env_ops=self.defaults_env_ops)

        self.state: str = "IDLE"
        self._watch_thread: Optional[threading.Thread] = None
        self._stop_watch = threading.Event()

    # -------- 状態遷移API --------
    def activate(self) -> None:
        if self.state not in ("IDLE", "TERMINATED"):
            print(f"[launcher] activate: invalid state={self.state}", file=sys.stderr)
            return
        # activate()は冪等ではない。再実行の場合はモニターを再生成する
        if self.state == "TERMINATED":
            self.monitor = HakoMonitor(self.spec, defaults_env_ops=self.defaults_env_ops)

        print("[INFO] activating 'before_start' assets...")
        self.state = "ACTIVATING"
        try:
            self.monitor.start_assets("before_start")
        except Exception:
            self.terminate()
            raise
        self._stop_watch.clear()
        self._watch_thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._watch_thread.start()
        self.state = "ACTIVATED"
        print("[INFO] state -> ACTIVATED")

    def cmd(self, command: str) -> int:
        if self.state not in ("ACTIVATED", "RUNNING", "STOPPED"):
            print(f"[launcher] start: invalid state={self.state}", file=sys.stderr)
            return 2
        print(f"[INFO] starting simulation (hako-cmd {command})...")
        if command not in ("start", "stop", "reset"):
            return 1
        rc = 1
        match command:
            case "start":
                rc = self.cli.start()
                if rc == 0:
                    print("[INFO] activating 'after_start' assets...")
                    self.monitor.start_assets("after_start")
                self.state = "RUNNING"
                print(f"[INFO] hako-cmd start exited with {rc}")
            case "stop":
                rc = self.cli.stop()
                self.state = "STOPPED"
                print(f"[INFO] hako-cmd stop exited with {rc}")
            case "reset":
                rc = self.cli.reset()
                self.state = "ACTIVATED"
                print(f"[INFO] hako-cmd reset exited with {rc}")
        return rc

    def terminate(self) -> None:
        if self.state == "TERMINATED":
            print(f"[launcher] terminate: already {self.state}")
            return
        if self.state == "IDLE" and not self.monitor.procs:
            print("[launcher] terminate: already IDLE")
            return
        print("[INFO] terminating all assets...")
        try:
            self.monitor.abort("terminate")
        finally:
            self._stop_watch.set()
            self.state = "TERMINATED"
            print("[INFO] state -> TERMINATED")

    def status(self) -> str:
        return self.state

    # -------- 内部：監視ループ（非ブロッキング） --------
    def _watch_loop(self):
        try:
            while not self._stop_watch.is_set() and self.monitor.procs:
                for rp in list(self.monitor.procs):
                    if not rp.runner.is_alive():
                        print(f"[WARN] asset exited: {rp.asset.name} -> abort all")
                        self.monitor.abort("asset_exit")
                        self.state = "TERMINATED"
                        self._stop_watch.set()
                        return
                time.sleep(0.2)
        except Exception as e:
            print(f"[watch] exception: {e}", file=sys.stderr)
            self.monitor.abort("watch_exception")
            self.state = "TERMINATED"
            self._stop_watch.set()


# -------- background lifecycle --------

def _background_log_path(session_file: Path) -> Path:
    return Path(f"{session_file}.log")


def _install_sigint(service: LauncherService):
    def _signal_handler(signum, frame):
        print(f"[launcher] signal({signum}) received → aborting...")
        try:
            service.terminate()
        finally:
            sys.exit(1)

    signal.signal(signal.SIGINT, _signal_handler)
    if hasattr(signal, "SIGBREAK"):
        signal.signal(signal.SIGBREAK, _signal_handler)


def _stop_background_process(proc: subprocess.Popen) -> None:
    try:
        if os.name == "nt" and hasattr(signal, "CTRL_BREAK_EVENT"):
            proc.send_signal(signal.CTRL_BREAK_EVENT)
        else:
            proc.send_signal(signal.SIGINT)
        proc.wait(timeout=_BACKGROUND_SHUTDOWN_TIMEOUT_SEC)
    except subprocess.TimeoutExpired:
        try:
            proc.kill()
            proc.wait(timeout=5)
        except Exception:
            pass
    except Exception:
        pass


def _starting_session_payload(
    *,
    session_id: str,
    launch_path: Path,
    log_path: Path,
    pid: int,
) -> dict:
    return {
        "version": 1,
        "session_id": session_id,
        "pid": pid,
        "launch_file": str(launch_path),
        "log_file": str(log_path),
        "state": "STARTING",
    }


def _reserve_background_session(
    *,
    launch_path: Path,
    session_path: Path,
    log_path: Path,
) -> tuple[str | None, int]:
    session_id = new_session_id()
    try:
        claim_session(
            session_path,
            _starting_session_payload(
                session_id=session_id,
                launch_path=launch_path,
                log_path=log_path,
                pid=os.getpid(),
            ),
        )
    except FileExistsError:
        print(
            f"[launcher] another launcher reserved the session file: {session_path}",
            file=sys.stderr,
        )
        return None, 2
    except LauncherControlError as exc:
        print(f"[launcher] {exc}", file=sys.stderr)
        return None, 2
    except OSError as exc:
        print(f"[launcher] cannot reserve session file {session_path}: {exc}", file=sys.stderr)
        return None, 1
    return session_id, 0


def _spawn_background(launch_file: str, session_file: str) -> int:
    launch_path = Path(launch_file).expanduser().resolve()
    session_path = Path(session_file).expanduser().resolve()
    log_path = _background_log_path(session_path)
    session_path.parent.mkdir(parents=True, exist_ok=True)

    session_id, reserve_rc = _reserve_background_session(
        launch_path=launch_path,
        session_path=session_path,
        log_path=log_path,
    )
    if session_id is None:
        return reserve_rc

    command = [
        sys.executable,
        "-m",
        "hakoniwa_pdu.apps.launcher.hako_launcher",
        str(launch_path),
        "--_background-worker",
        str(session_path),
        f"--_session-id={session_id}",
    ]
    popen_kwargs = {
        "stdin": subprocess.DEVNULL,
        "stderr": subprocess.STDOUT,
        "close_fds": True,
    }
    if os.name == "nt":
        popen_kwargs["creationflags"] = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    else:
        popen_kwargs["start_new_session"] = True

    try:
        with log_path.open("w", encoding="utf-8") as log_stream:
            popen_kwargs["stdout"] = log_stream
            proc = subprocess.Popen(command, **popen_kwargs)
    except OSError as exc:
        _write_failed_session(
            session_path,
            launch_path,
            log_path,
            f"failed to start background launcher: {exc}",
            session_id=session_id,
            pid=os.getpid(),
        )
        print(f"[launcher] failed to start background launcher: {exc}", file=sys.stderr)
        return 1

    write_owned_session(
        session_path,
        _starting_session_payload(
            session_id=session_id,
            launch_path=launch_path,
            log_path=log_path,
            pid=proc.pid,
        ),
        session_id=session_id,
    )

    deadline = time.monotonic() + _BACKGROUND_READY_TIMEOUT_SEC
    while time.monotonic() < deadline:
        if session_path.exists():
            try:
                session = read_session(session_path)
                if session.get("session_id") != session_id:
                    print(
                        f"[launcher] session ownership changed during startup: {session_path}",
                        file=sys.stderr,
                    )
                    _stop_background_process(proc)
                    return 1
                state = str(session.get("state", "UNKNOWN"))
                if state == "FAILED":
                    print(
                        f"[launcher] background launcher failed: {session.get('error', 'unknown error')} "
                        f"(log={log_path})",
                        file=sys.stderr,
                    )
                    return 1
                if state != "STARTING":
                    response = send_control_command(session_path, "status", timeout_sec=1.0)
                    print(
                        json.dumps(
                            {
                                "session_file": str(session_path),
                                "pid": response.get("pid"),
                                "state": response.get("state"),
                                "log_file": str(log_path),
                            }
                        )
                    )
                    return 0
            except LauncherControlError:
                pass
        rc = proc.poll()
        if rc is not None:
            _write_failed_session(
                session_path,
                launch_path,
                log_path,
                f"background launcher exited before becoming ready: rc={rc}",
                session_id=session_id,
                pid=proc.pid,
            )
            print(
                f"[launcher] background launcher exited before becoming ready: rc={rc} "
                f"(log={log_path})",
                file=sys.stderr,
            )
            return 1
        time.sleep(0.1)

    print(
        f"[launcher] timed out waiting for background launcher readiness "
        f"(log={log_path})",
        file=sys.stderr,
    )
    _stop_background_process(proc)
    _write_failed_session(
        session_path,
        launch_path,
        log_path,
        "timed out waiting for background launcher readiness",
        session_id=session_id,
        pid=proc.pid,
    )
    return 1


def _write_failed_session(
    session_file: Path,
    launch_file: Path,
    log_file: Path,
    error: str,
    *,
    session_id: str,
    pid: int | None = None,
) -> None:
    write_owned_session(
        session_file,
        {
            "version": 1,
            "session_id": session_id,
            "pid": os.getpid() if pid is None else pid,
            "launch_file": str(launch_file),
            "log_file": str(log_file),
            "state": "FAILED",
            "error": error,
        },
        session_id=session_id,
    )


def _run_background_worker(
    service: LauncherService,
    launch_file: str,
    session_file: str,
    session_id: str,
) -> int:
    session_path = Path(session_file).expanduser().resolve()
    launch_path = Path(launch_file).expanduser().resolve()
    log_path = _background_log_path(session_path)
    server: LauncherControlServer | None = None
    try:
        service.activate()
        rc = service.cmd("start")
        if rc != 0:
            raise RuntimeError(f"hako-cmd start failed with rc={rc}")
        server = LauncherControlServer(
            service=service,
            session_path=session_path,
            launch_file=launch_path,
            log_file=log_path,
            session_id=session_id,
        )
        server.serve_until_terminated()
        return 0
    except Exception as exc:
        try:
            service.terminate()
        except Exception:
            pass
        _write_failed_session(
            session_path,
            launch_path,
            log_path,
            str(exc),
            session_id=session_id,
        )
        print(f"[launcher] background worker failed: {exc}", file=sys.stderr)
        return 1
    finally:
        if server is not None:
            server.server_close()


# -------- CLI エントリ --------

async def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Hakoniwa Launcher")
    parser.add_argument("launch_file", help="Path to launcher JSON")
    parser.add_argument(
        "--mode",
        choices=["immediate", "activate-only", "serve"],
        default="immediate",
        help="immediate: activate→start→watch / activate-only: activateだけ実行して待機 / serve: 待機して外部コマンドを受け付ける",
    )
    parser.add_argument("--no-watch", action="store_true",
                        help="(immediate時) 監視せず起動だけして終了")
    parser.add_argument(
        "--background",
        metavar="SESSION_FILE",
        help="Launch in the background and write lifecycle control information to SESSION_FILE",
    )
    parser.add_argument("--_background-worker", metavar="SESSION_FILE", help=argparse.SUPPRESS)
    parser.add_argument("--_session-id", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    if args.background is not None:
        if args.mode != "immediate" or args.no_watch:
            parser.error("--background cannot be combined with --mode or --no-watch")
        return _spawn_background(args.launch_file, args.background)
    if args._background_worker is not None and args._session_id is None:
        parser.error("--_session-id is required for a background worker")

    # Setup logging
    if os.environ.get('HAKO_PDU_DEBUG') == '1':
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stdout
    )

    try:
        service = LauncherService(launch_path=args.launch_file)
    except Exception as e:
        if args._background_worker is not None:
            session_path = Path(args._background_worker).expanduser().resolve()
            launch_path = Path(args.launch_file).expanduser().resolve()
            _write_failed_session(
                session_path,
                launch_path,
                _background_log_path(session_path),
                f"failed to load spec: {e}",
                session_id=args._session_id,
            )
        print(f"[launcher] Failed to load spec: {e}", file=sys.stderr)
        return 1

    _install_sigint(service)

    print("[INFO] HakoLauncher ready. assets:")
    for a in service.spec.assets:
        print(f" - {a.name} (cwd={a.cwd}, cmd={a.command}, args={a.args})")

    if args._background_worker is not None:
        return _run_background_worker(
            service,
            args.launch_file,
            args._background_worker,
            args._session_id,
        )

    if args.mode == "immediate":
        try:
            service.activate()
            rc = service.cmd("start")
            if not args.no_watch:
                while service.status() not in ("TERMINATED",):
                    time.sleep(0.5)
            return 0 if rc == 0 else rc
        except Exception as e:
            print(f"[launcher] Exception: {e}", file=sys.stderr)
            service.terminate()
            return 1

    elif args.mode == "activate-only":
        try:
            service.activate()
            while service.status() not in ("TERMINATED",):
                time.sleep(0.5)
            return 0
        except Exception as e:
            print(f"[launcher] Exception: {e}", file=sys.stderr)
            service.terminate()
            return 1

    elif args.mode == "serve":
        print("[INFO] serve mode. commands: activate | start | stop | reset | terminate | status | quit")
        while True:
            try:
                sys.stdout.write("> ")
                sys.stdout.flush()
                line = sys.stdin.readline()
                if not line:
                    break
                cmd = line.strip().lower()
                if cmd == "activate":
                    service.activate()
                elif cmd == "start":
                    service.cmd("start")
                elif cmd == "stop":
                    service.cmd("stop")
                elif cmd == "reset":
                    service.cmd("reset")
                elif cmd == "terminate":
                    service.terminate()
                elif cmd == "status":
                    print(service.status())
                elif cmd in ("quit", "exit"):
                    service.terminate()
                    break
                elif cmd == "":
                    continue
                else:
                    print(f"unknown command: {cmd}")
            except KeyboardInterrupt:
                service.terminate()
                break
            except Exception as e:
                print(f"[serve] error: {e}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
