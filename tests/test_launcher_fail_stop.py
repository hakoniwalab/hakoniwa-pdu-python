from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
import subprocess
import threading

import pytest

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
            stdout=json.dumps({"status": "ABORT", "reason": "owner died"}),
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    health = cli.check(timeout=0.25)
    assert health.status == "ABORT"
    assert health.reason == "owner died"


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
