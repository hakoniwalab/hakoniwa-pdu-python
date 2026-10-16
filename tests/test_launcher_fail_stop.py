from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
import subprocess
import threading
import time

import pytest

from hakoniwa_pdu.apps.launcher import hako_launcher
from hakoniwa_pdu.apps.launcher.hako_cli import HakoCli, RuntimeHealth
from hakoniwa_pdu.apps.launcher.hako_launcher import LauncherService
from hakoniwa_pdu.apps.launcher.hako_launcher_control import (
    LauncherControlServer,
    read_session,
    reserve_session,
)


class Result:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def test_hako_cli_check_parses_abort(monkeypatch, tmp_path):
    cli = HakoCli(SimpleNamespace(base_dir=tmp_path))
    monkeypatch.setattr(cli, "_resolve_cmd", lambda env: "hako-cmd")

    def fake_run(command, **kwargs):
        if "--version" in command:
            return Result(stdout="hako-cmd version 1.1.0\n")
        assert command == ["hako-cmd", "check"]
        assert kwargs["timeout"] == 0.25
        return Result(
            returncode=2,
            stdout=json.dumps({
                "schema_version": 1,
                "status": "ABORT",
                "reason": "owner died",
                "checks": [
                    {"name": "master_lock", "status": "ABORT", "reason": "owner died"}
                ],
            }),
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    health = cli.check(timeout=0.25)
    assert health.status == "ABORT"
    assert health.reason == "owner died"


def test_hako_cli_check_rejects_unversioned_report(monkeypatch, tmp_path):
    cli = HakoCli(SimpleNamespace(base_dir=tmp_path))
    cli._detected_version = (1, 1, 0)
    cli._bounded_lock_wait_supported = True
    monkeypatch.setattr(cli, "_resolve_cmd", lambda env: "hako-cmd")
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: Result(
            returncode=0,
            stdout=json.dumps({"status": "OK", "reason": "old", "checks": {}}),
        ),
    )
    health = cli.check(timeout=0.25)
    assert health.status == "UNKNOWN"
    assert "unsupported schema" in health.reason


def test_hako_cli_check_timeout_is_unknown(monkeypatch, tmp_path):
    cli = HakoCli(SimpleNamespace(base_dir=tmp_path))
    cli._detected_version = (1, 1, 0)
    cli._bounded_lock_wait_supported = True
    monkeypatch.setattr(cli, "_resolve_cmd", lambda env: "hako-cmd")

    def fake_run(command, **kwargs):
        raise subprocess.TimeoutExpired(command, kwargs["timeout"])

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert cli.check(timeout=0.1).status == "UNKNOWN"


class Monitor:
    def __init__(self):
        self.procs = []
        self.start_calls = []
        self.abort_calls = []

    def start_assets(self, timing):
        self.start_calls.append(timing)

    def abort(self, reason):
        self.abort_calls.append(reason)


def bare_service(health: RuntimeHealth) -> LauncherService:
    service = object.__new__(LauncherService)
    service.state = "IDLE"
    service.monitor = Monitor()
    service.cli = SimpleNamespace(check=lambda **kwargs: health)
    service._stop_watch = threading.Event()
    service._watch_thread = None
    service._cli_prepared = True
    service._health_check_interval_sec = 1.0
    service._health_check_timeout_sec = 0.1
    service._last_unknown_health_reason = None
    service._last_health_report = None
    service.failure_report = None
    service._prepare_cli = lambda: None
    service._prepare_runtime = lambda: None
    return service


def test_startup_abort_fails_before_spawning_assets():
    service = bare_service(RuntimeHealth("ABORT", "owner died", {}))
    with pytest.raises(RuntimeError, match="returned ABORT"):
        service.activate()
    assert service.state == "FAILED"
    assert service.monitor.start_calls == []
    assert service.failure_report["reason"] == "owner died"


def test_startup_unknown_warns_and_continues(capsys):
    service = bare_service(RuntimeHealth("UNKNOWN", "legacy metadata", {}))
    service.activate()
    assert service.state == "ACTIVATED"
    assert service.monitor.start_calls == ["before_start"]
    assert "UNKNOWN" in capsys.readouterr().err
    service.terminate()


def test_fail_stop_preserves_failed_state_and_stops_assets():
    service = bare_service(RuntimeHealth("ABORT", "owner died", {}))
    service.state = "RUNNING"
    service._fail_stop("runtime_integrity_abort")
    assert service.state == "FAILED"
    assert service.monitor.abort_calls == ["runtime_integrity_abort"]
    assert service._stop_watch.is_set()
    assert service.failure_report["trigger"] == "runtime_integrity_abort"


def test_periodic_abort_transitions_to_failed_and_stops_monitor():
    service = bare_service(RuntimeHealth("ABORT", "owner died", {"generation": 7}))
    service.state = "RUNNING"
    service._health_check_interval_sec = 0.01
    watcher = threading.Thread(target=service._watch_loop)
    watcher.start()
    watcher.join(timeout=2)
    assert not watcher.is_alive()
    assert service.state == "FAILED"
    assert service.monitor.abort_calls == ["runtime_integrity_abort"]
    assert service.failure_report["details"]["generation"] == 7


def test_fail_stop_does_not_delete_diagnostic_files(tmp_path):
    evidence = tmp_path / "flock.bin"
    evidence.write_bytes(b"diagnostic evidence")
    service = bare_service(RuntimeHealth("ABORT", "owner died", {}))
    service._last_health_report = {
        "status": "ABORT", "reason": "owner died", "details": {}
    }
    service._fail_stop("runtime_integrity_abort")
    assert evidence.read_bytes() == b"diagnostic evidence"


def test_background_session_persists_failure_report(tmp_path):
    service = bare_service(RuntimeHealth("ABORT", "owner died", {"owner_pid": 42}))
    service._check_runtime_health()
    service._fail_stop("runtime_integrity_abort")
    session = tmp_path / "session.json"
    reserve_session(session, {"session_id": "test", "state": "STARTING"})
    server = LauncherControlServer(
        service=service,
        session_path=session,
        launch_file=tmp_path / "launch.json",
        log_file=tmp_path / "launcher.log",
        session_id="test",
    )
    try:
        server.persist(force=True)
        payload = read_session(session)
        assert payload["state"] == "FAILED"
        assert payload["failure_report"]["reason"] == "owner died"
        assert payload["failure_report"]["details"]["owner_pid"] == 42
    finally:
        server.server_close()


def test_cleanup_on_start_is_refused_by_fail_stop_policy():
    service = object.__new__(LauncherService)
    service.launcher_spec = SimpleNamespace(
        runtime=SimpleNamespace(cleanup_mmap_on_start=True)
    )
    with pytest.raises(RuntimeError, match="hako-cmd recover"):
        service._prepare_runtime()


def test_unexpected_asset_exit_stays_failed_and_records_exit():
    class DeadRunner:
        def is_alive(self):
            return False

        def exit_info(self):
            return SimpleNamespace(pid=321, exit_code=9, signal=None)

        def diagnostics(self):
            return {
                "pid": 321,
                "alive": False,
                "exit_code": 9,
                "signal": None,
                "cleanup_scope": "posix_process_group",
                "descendants_verified_stopped": True,
            }

    service = bare_service(RuntimeHealth("OK", "healthy", {}))
    service.state = "RUNNING"
    service.monitor.procs = [
        SimpleNamespace(asset=SimpleNamespace(name="failed-asset"), runner=DeadRunner())
    ]

    service._watch_loop()

    assert service.state == "FAILED"
    assert service.failure_report["trigger"] == "unexpected_asset_exit"
    assert service.failure_report["asset_exit"] == {
        "asset": "failed-asset",
        "pid": 321,
        "exit_code": 9,
        "signal": None,
    }
    assert service.failure_report["cleanup"]["status"] == "OK"


def test_fail_stop_records_cleanup_exception_and_survivor():
    class LiveRunner:
        def is_alive(self):
            return True

        def diagnostics(self):
            return {
                "pid": 654,
                "alive": True,
                "exit_code": None,
                "signal": None,
                "cleanup_scope": "direct_process",
                "descendants_verified_stopped": False,
            }

    class FailingMonitor(Monitor):
        def __init__(self):
            super().__init__()
            self.procs = [
                SimpleNamespace(asset=SimpleNamespace(name="survivor"), runner=LiveRunner())
            ]

        def abort(self, reason):
            raise RuntimeError("kill denied")

    service = bare_service(RuntimeHealth("ABORT", "owner died", {}))
    service.monitor = FailingMonitor()
    service._last_health_report = {
        "status": "ABORT",
        "reason": "owner died",
        "details": {"owner_pid": 42},
        "detected_at": time.time(),
    }

    service._fail_stop("runtime_integrity_abort")

    cleanup = service.failure_report["cleanup"]
    assert service.state == "FAILED"
    assert cleanup["status"] == "FAILED"
    assert cleanup["exception"] == "kill denied"
    assert cleanup["survivors"][0]["asset"] == "survivor"
    assert cleanup["recover_safe"] is False
    assert "do not run hako-cmd recover" in cleanup["recovery_guidance"]


def test_terminate_after_failure_does_not_overwrite_failed_state():
    service = bare_service(RuntimeHealth("ABORT", "owner died", {}))
    service.state = "FAILED"
    service.failure_report = {"trigger": "runtime_integrity_abort"}

    service.terminate()

    assert service.state == "FAILED"
    assert service.failure_report["trigger"] == "runtime_integrity_abort"


def test_background_startup_abort_preserves_failure_report(tmp_path):
    class StartupAbortService:
        state = "IDLE"
        failure_report = None

        def activate(self, *, require_hako_cmd=True):
            self.state = "FAILED"
            self.failure_report = {
                "status": "ABORT",
                "reason": "owner died",
                "details": {"owner_pid": 42},
                "detected_at": 123.0,
                "trigger": "startup_runtime_integrity_abort",
                "cleanup": {"status": "OK", "recover_safe": True},
            }
            raise RuntimeError("Hakoniwa runtime integrity check returned ABORT")

        def status(self):
            return self.state

        def terminate(self):
            raise AssertionError("FAILED startup must not be overwritten by terminate")

    session = tmp_path / "session.json"
    reserve_session(session, {"session_id": "startup-abort", "state": "STARTING"})
    service = StartupAbortService()

    rc = hako_launcher._run_background_worker(
        service,
        str(tmp_path / "launch.json"),
        str(session),
        "startup-abort",
        "immediate",
    )

    payload = read_session(session)
    assert rc == 1
    assert payload["state"] == "FAILED"
    assert payload["failure_report"]["status"] == "ABORT"
    assert payload["failure_report"]["details"]["owner_pid"] == 42
    assert payload["failure_report"]["cleanup"]["status"] == "OK"
