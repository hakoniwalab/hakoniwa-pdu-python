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
from .envmerge import merge_env
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
BACKGROUND_MODES = ("immediate", "activate-only")


# Fail-stop triggers found by the runtime health check (their report is the reason).
_HEALTH_TRIGGERS = frozenset({"startup_runtime_integrity_abort", "runtime_integrity_abort"})
# How long a process ending on FAILED waits for the cleanup (asset stop has its own timeouts).
_FAILURE_CLEANUP_WAIT_SEC = 60.0


def _trigger_reason(trigger: str, evidence: Optional[dict]) -> str:
    exit_info = (evidence or {}).get("asset_exit")
    if trigger == "unexpected_asset_exit" and isinstance(exit_info, dict):
        how = (f"signal {exit_info.get('signal')}" if exit_info.get("signal") is not None
               else f"exit code {exit_info.get('exit_code')}")
        return f"asset {exit_info.get('asset')} exited unexpectedly ({how})"
    if trigger == "watch_exception":
        return f"the Launcher watch failed: {(evidence or {}).get('watch_exception')}"
    return trigger


class LauncherService:
    """起動・監視・停止を状態付きで提供。"""

    _sync_init_lock = threading.Lock()

    def __init__(self, *, launch_path: str) -> None:
        self.launcher_spec, self.spec = load(launch_path)  # (LauncherSpec, EffectiveSpec)
        self.defaults_env_ops = None
        if self.launcher_spec.defaults and self.launcher_spec.defaults.env:
            self.defaults_env_ops = self.launcher_spec.defaults.env.model_dump(exclude_none=True)

        self.cli     = HakoCli(spec=self.spec, defaults_env_ops=self.defaults_env_ops)
        self.monitor = HakoMonitor(
            self.spec,
            defaults_env_ops=self.defaults_env_ops,
            asset_list_provider=self.cli,
        )

        self.state: str = "IDLE"
        self._state_lock = threading.RLock()
        self._failure_cleanup_started = False
        # Set while no fail-stop cleanup runs; the process must not exit before it is.
        self._failure_cleanup_done = threading.Event()
        self._failure_cleanup_done.set()
        self._watch_thread: Optional[threading.Thread] = None
        self._stop_watch = threading.Event()
        self._cli_prepared = False
        runtime = self.launcher_spec.runtime
        self._health_check_interval_sec = float(
            runtime.health_check_interval_sec if runtime is not None else 1.0
        )
        self._health_check_timeout_sec = float(
            runtime.health_check_timeout_sec if runtime is not None else 3.0
        )
        self._last_unknown_health_reason: Optional[str] = None
        self._last_health_report: Optional[dict] = None
        self.failure_report: Optional[dict] = None

    def _state_mutex(self) -> threading.RLock:
        """Return the lifecycle mutex, including for lightweight test doubles."""
        lock = getattr(self, "_state_lock", None)
        if lock is not None:
            return lock
        with self._sync_init_lock:
            lock = getattr(self, "_state_lock", None)
            if lock is None:
                lock = threading.RLock()
                self._state_lock = lock
            if not hasattr(self, "_failure_cleanup_started"):
                self._failure_cleanup_started = False
        return lock

    def _prepare_cli(self) -> None:
        if self._cli_prepared:
            return
        version, bounded_lock_wait = self.cli.prepare()
        version_text = ".".join(str(value) for value in version) if version else "unknown"
        if bounded_lock_wait:
            print(
                f"[INFO] hako-cmd {version_text}: bounded file-lock waits enabled"
            )
        else:
            print(
                f"[WARN] hako-cmd {version_text}: legacy compatibility mode; "
                "readiness uses only the Python subprocess timeout",
                file=sys.stderr,
            )
        self._cli_prepared = True

    def _prepare_runtime(self) -> None:
        runtime = self.launcher_spec.runtime
        if runtime is None or not runtime.cleanup_mmap_on_start:
            return
        raise RuntimeError(
            "runtime.cleanup_mmap_on_start is disabled by fail-stop policy; "
            "inspect with 'hako-cmd check' and explicitly run "
            "'hako-cmd recover' only after confirming all processes stopped"
        )

    def _check_runtime_health(self, *, startup: bool = False) -> str:
        health = self.cli.check(timeout=self._health_check_timeout_sec)
        self._last_health_report = {
            "status": health.status,
            "reason": health.reason,
            "details": health.details,
            "detected_at": time.time(),
        }
        if health.status == "ABORT":
            print(
                f"[ERROR] Hakoniwa runtime integrity ABORT: {health.reason}",
                file=sys.stderr,
            )
            return "ABORT"
        if health.status == "UNKNOWN":
            if startup or health.reason != self._last_unknown_health_reason:
                print(
                    f"[WARN] Hakoniwa runtime integrity UNKNOWN: {health.reason}",
                    file=sys.stderr,
                )
            self._last_unknown_health_reason = health.reason
            return "UNKNOWN"
        self._last_unknown_health_reason = None
        return "OK"

    def _managed_process_diagnostics(self) -> list[dict]:
        diagnostics: list[dict] = []
        for running in list(self.monitor.procs):
            runner = running.runner
            try:
                detail = runner.diagnostics() if hasattr(runner, "diagnostics") else {
                    "alive": bool(runner.is_alive()),
                }
            except Exception as exc:
                detail = {
                    "alive": None,
                    "diagnostic_error": str(exc),
                    "descendants_verified_stopped": False,
                }
            diagnostics.append({"asset": running.asset.name, **detail})
        return diagnostics

    def _cleanup_after_failure(self, reason: str) -> dict:
        cleanup_error: str | None = None
        try:
            self.monitor.abort(reason)
        except Exception as exc:
            cleanup_error = str(exc)
            print(f"[ERROR] fail-stop cleanup failed: {exc}", file=sys.stderr)

        processes = self._managed_process_diagnostics()
        survivors = [
            process for process in processes if process.get("alive") is not False
        ]
        unverified_descendants = [
            process for process in processes
            if process.get("descendants_verified_stopped") is False
        ]
        recover_safe = (
            cleanup_error is None
            and not survivors
            and not unverified_descendants
        )
        return {
            "status": "OK" if cleanup_error is None and not survivors else "FAILED",
            "reason": cleanup_error or (
                "managed processes stopped"
                if not survivors
                else "one or more managed processes may still be alive"
            ),
            "exception": cleanup_error,
            "processes": processes,
            "survivors": survivors,
            "recover_safe": recover_safe,
            "recovery_guidance": (
                "all managed processes and descendants were verified stopped"
                if recover_safe
                else "do not run hako-cmd recover until remaining or unverified "
                     "processes are checked and stopped"
            ),
        }

    def _fail_stop(self, reason: str, *, evidence: Optional[dict] = None) -> None:
        # FAILED is monotonic for a session.  Only the first failure owns
        # cleanup and its evidence; later observers must not replace either.
        with self._state_mutex():
            if self.state == "FAILED" and self.failure_report is not None:
                return
            last_health = getattr(self, "_last_health_report", None) or {}
            if reason in _HEALTH_TRIGGERS:
                # The health check found the failure: its report is the reason.
                report = {**last_health, "trigger": reason}
            else:
                # Another trigger: the last periodic check (often UNKNOWN "lock
                # busy" while the master runs) is context, not the reason.
                report = {"trigger": reason, "reason": _trigger_reason(reason, evidence)}
                if last_health:
                    report["last_health_check"] = last_health
            self.failure_report = {**report, **(evidence or {})}
            self.state = "FAILED"
            self._stop_watch.set()
            if self._failure_cleanup_started:
                return
            self._failure_cleanup_started = True
            done = self._cleanup_done_event()
            done.clear()

        try:
            cleanup = self._cleanup_after_failure(reason)
            with self._state_mutex():
                assert self.failure_report is not None
                self.failure_report["cleanup"] = cleanup
                self.state = "FAILED"
        finally:
            done.set()

    def _cleanup_done_event(self) -> threading.Event:
        event = getattr(self, "_failure_cleanup_done", None)
        if event is None:  # lightweight test doubles
            event = threading.Event()
            event.set()
            self._failure_cleanup_done = event
        return event

    def wait_for_failure_cleanup(self, timeout: Optional[float] = _FAILURE_CLEANUP_WAIT_SEC) -> bool:
        """Wait until a running fail-stop cleanup has finished. FAILED is set
        before the cleanup starts (so nothing else starts); a process that ends
        on FAILED must wait here, or it would end the cleanup thread (a daemon)
        and leave assets running. True when no cleanup is running."""
        done = self._cleanup_done_event()
        if done.wait(timeout):
            return True
        print(f"[ERROR] fail-stop cleanup did not finish within {timeout} s", file=sys.stderr)
        return False

    def _failed(self) -> bool:
        with self._state_mutex():
            return self.state == "FAILED"

    def _transition_if(self, expected: str, target: str) -> bool:
        """Apply a lifecycle transition unless another thread moved the state."""
        with self._state_mutex():
            if self.state != expected or self.state == "FAILED":
                return False
            self.state = target
            return True

    # -------- 状態遷移API --------
    def activate(self, *, require_hako_cmd: bool = True) -> None:
        with self._state_mutex():
            if self.state not in ("IDLE", "TERMINATED"):
                print(f"[launcher] activate: invalid state={self.state}", file=sys.stderr)
                return
            # activate()は冪等ではない。再実行の場合はモニターを再生成する
            if self.state == "TERMINATED":
                self.monitor = HakoMonitor(
                    self.spec,
                    defaults_env_ops=self.defaults_env_ops,
                    asset_list_provider=self.cli,
                )
            self._stop_watch.clear()
            self._failure_cleanup_started = False
            self.failure_report = None
            self.state = "ACTIVATING"

        # Preserve the historical fail-fast hako-cmd check for normal
        # activation paths. activate-only can explicitly opt out so that
        # process-only/Core-free launch files do not need Hakoniwa Core.
        if require_hako_cmd:
            self._prepare_cli()
            if self._check_runtime_health(startup=True) == "ABORT":
                self._fail_stop("startup_runtime_integrity_abort")
                raise RuntimeError("Hakoniwa runtime integrity check returned ABORT")
        self._prepare_runtime()

        if self._failed():
            return

        print("[INFO] activating 'before_start' assets...")
        try:
            self.monitor.start_assets("before_start")
        except Exception:
            if not self._failed():
                self.terminate()
            raise
        if self._failed():
            return
        self._watch_thread = threading.Thread(target=self._watch_loop, daemon=True)
        if not self._transition_if("ACTIVATING", "ACTIVATED"):
            return
        print("[INFO] state -> ACTIVATED")
        self._watch_thread.start()

    def cmd(self, command: str) -> int:
        with self._state_mutex():
            initial_state = self.state
            if initial_state not in ("ACTIVATED", "RUNNING", "STOPPED"):
                print(f"[launcher] start: invalid state={initial_state}", file=sys.stderr)
                return 2
        if command not in ("start", "stop", "reset"):
            return 1
        # Lifecycle commands are the point where hako-cmd becomes mandatory.
        # Keeping this out of activate() lets activate-only manage Core-free
        # processes without installing Hakoniwa Core.
        self._prepare_cli()
        if self._failed():
            return 1
        print(f"[INFO] starting simulation (hako-cmd {command})...")
        rc = 1
        match command:
            case "start":
                rc = self.cli.start()
                if rc == 0 and not self._failed():
                    print("[INFO] activating 'after_start' assets...")
                    self.monitor.start_assets("after_start")
                self._transition_if(initial_state, "RUNNING")
                print(f"[INFO] hako-cmd start exited with {rc}")
            case "stop":
                rc = self.cli.stop()
                self._transition_if(initial_state, "STOPPED")
                print(f"[INFO] hako-cmd stop exited with {rc}")
            case "reset":
                rc = self.cli.reset()
                self._transition_if(initial_state, "ACTIVATED")
                print(f"[INFO] hako-cmd reset exited with {rc}")
        return rc

    def terminate(self) -> None:
        with self._state_mutex():
            if self.state == "IDLE" and not self.monitor.procs:
                print("[launcher] terminate: already IDLE")
                return
            preserve_failed = self.state == "FAILED"
            if self.state == "TERMINATED":
                print("[launcher] terminate: verifying terminated assets...")
            else:
                print("[INFO] terminating all assets...")
            if not preserve_failed:
                self.state = "TERMINATING"
            self._stop_watch.set()
        try:
            self.monitor.abort("terminate")
        except Exception:
            with self._state_mutex():
                self.state = "FAILED"
            print("[ERROR] asset cleanup failed; state -> FAILED", file=sys.stderr)
            raise
        else:
            with self._state_mutex():
                if self.state != "FAILED" and not preserve_failed:
                    self.state = "TERMINATED"
                final_state = self.state
            print(f"[INFO] state -> {final_state}")
            if final_state == "TERMINATED" and not preserve_failed:
                self._recover_after_normal_stop()

    def _recover_after_normal_stop(self) -> None:
        """A requested stop terminates the assets; one that was holding the master lock at that moment
        leaves it recorded as held by a dead owner, and the next start would fail-stop on it (an Urban
        car plant is the master and takes the lock every step). That is not a crash: when every managed
        process is stopped and the dead owner is one of them, clear the runtime with `hako-cmd recover`
        (which itself refuses while a recorded Hakoniwa process lives). A FAILED session, or an owner this
        Launcher did not run, keeps its evidence."""
        if not getattr(self, "_cli_prepared", False):
            return
        processes = self._managed_process_diagnostics()
        if any(process.get("alive") is not False for process in processes):
            print("[WARN] normal stop: a managed process may still be alive; runtime not recovered",
                  file=sys.stderr)
            return
        try:
            health = self.cli.check(timeout=self._health_check_timeout_sec)
        except Exception as exc:  # diagnosis only; never fail the stop
            print(f"[WARN] normal stop: hako-cmd check failed: {exc}", file=sys.stderr)
            return
        if health.status != "ABORT":
            return
        owners = {check.get("owner_pid") for check in health.details.get("checks", [])
                  if isinstance(check, dict) and check.get("status") == "ABORT"}
        managed = {process.get("pid") for process in processes if process.get("pid")}
        if not owners or not owners <= managed:
            print(f"[WARN] normal stop: the master lock owner {sorted(owners)} was not run by this "
                  "Launcher; runtime left for diagnosis", file=sys.stderr)
            return
        rc, report = self.cli.recover()
        if rc == 0:
            print(f"[INFO] normal stop: cleared the lock left by stopped asset(s) {sorted(owners)} "
                  "(hako-cmd recover)")
        else:
            print(f"[WARN] normal stop: hako-cmd recover returned {rc}: "
                  f"{report.get('reason', report.get('status', ''))}", file=sys.stderr)

    def status(self) -> str:
        with self._state_mutex():
            return self.state

    # -------- 内部：監視ループ（非ブロッキング） --------
    def _watch_loop(self):
        try:
            next_health_check = time.monotonic()
            while not self._stop_watch.is_set():
                for rp in list(self.monitor.procs):
                    if not rp.runner.is_alive():
                        exit_info = (
                            rp.runner.exit_info()
                            if hasattr(rp.runner, "exit_info")
                            else None
                        )
                        exit_code = getattr(exit_info, "exit_code", None)
                        exit_signal = getattr(exit_info, "signal", None)
                        if exit_code == 0 and exit_signal is None:
                            print(
                                f"[INFO] asset completed normally: "
                                f"{rp.asset.name} -> terminate all"
                            )
                            self.terminate()
                        else:
                            print(
                                f"[WARN] asset exited unexpectedly: "
                                f"{rp.asset.name} -> abort all"
                            )
                            self._fail_stop(
                                "unexpected_asset_exit",
                                evidence={
                                    "asset_exit": {
                                        "asset": rp.asset.name,
                                        "pid": getattr(exit_info, "pid", None),
                                        "exit_code": exit_code,
                                        "signal": exit_signal,
                                    }
                                },
                            )
                        return
                now = time.monotonic()
                if getattr(self, "_cli_prepared", False) and now >= next_health_check:
                    if self._check_runtime_health() == "ABORT":
                        self._fail_stop("runtime_integrity_abort")
                        return
                    next_health_check = now + self._health_check_interval_sec
                time.sleep(0.2)
        except Exception as e:
            print(f"[watch] exception: {e}", file=sys.stderr)
            self._fail_stop(
                "watch_exception",
                evidence={"watch_exception": str(e)},
            )


# -------- background lifecycle --------

def _wait_for_failure_cleanup(service) -> None:
    wait = getattr(service, "wait_for_failure_cleanup", None)
    if wait is not None:
        wait()


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


def _spawn_background(
    launch_file: str,
    session_file: str,
    *,
    mode: str = "immediate",
) -> int:
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
        f"--_background-mode={mode}",
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
    failure_report: dict | None = None,
) -> None:
    payload = {
        "version": 1,
        "session_id": session_id,
        "pid": os.getpid() if pid is None else pid,
        "launch_file": str(launch_file),
        "log_file": str(log_file),
        "state": "FAILED",
        "error": error,
    }
    if failure_report is not None:
        payload["failure_report"] = failure_report
    write_owned_session(
        session_file,
        payload,
        session_id=session_id,
    )


def _run_background_worker(
    service: LauncherService,
    launch_file: str,
    session_file: str,
    session_id: str,
    mode: str,
) -> int:
    session_path = Path(session_file).expanduser().resolve()
    launch_path = Path(launch_file).expanduser().resolve()
    log_path = _background_log_path(session_path)
    server: LauncherControlServer | None = None
    try:
        service.activate(require_hako_cmd=(mode != "activate-only"))
        if mode == "immediate":
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
        _wait_for_failure_cleanup(service)
        if service.status() != "FAILED":
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
            failure_report=service.failure_report,
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
    parser.add_argument(
        "--_background-mode",
        choices=BACKGROUND_MODES,
        default="immediate",
        help=argparse.SUPPRESS,
    )
    args = parser.parse_args(argv)

    if args.background is not None:
        if args.mode == "serve" or args.no_watch:
            parser.error("--background supports immediate or activate-only mode")
        return _spawn_background(args.launch_file, args.background, mode=args.mode)
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
            args._background_mode,
        )

    if args.mode == "immediate":
        try:
            service.activate()
            rc = service.cmd("start")
            if not args.no_watch:
                while service.status() not in ("TERMINATED", "FAILED"):
                    time.sleep(0.5)
            if service.status() == "FAILED":
                _wait_for_failure_cleanup(service)
                return 1
            return 0 if rc == 0 else rc
        except Exception as e:
            print(f"[launcher] Exception: {e}", file=sys.stderr)
            if service.status() != "FAILED":
                service.terminate()
            return 1

    elif args.mode == "activate-only":
        try:
            service.activate(require_hako_cmd=False)
            while service.status() not in ("TERMINATED", "FAILED"):
                time.sleep(0.5)
            if service.status() == "FAILED":
                _wait_for_failure_cleanup(service)
                return 1
            return 0
        except Exception as e:
            print(f"[launcher] Exception: {e}", file=sys.stderr)
            if service.status() != "FAILED":
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
