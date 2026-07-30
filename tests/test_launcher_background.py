import json
import threading

import pytest

from hakoniwa_pdu.apps.launcher import hako_launcher, hako_launcher_control
from hakoniwa_pdu.apps.launcher.hako_launcher_control import (
    LauncherControlError,
    LauncherControlServer,
    read_session,
    reserve_session,
    send_control_command,
    session_file_lock,
    write_session,
)


class FakeService:
    def __init__(self) -> None:
        self.state = "RUNNING"
        self.terminate_calls = 0

    def status(self) -> str:
        return self.state

    def terminate(self) -> None:
        self.terminate_calls += 1
        self.state = "TERMINATED"


def _run_server(server: LauncherControlServer) -> threading.Thread:
    reserve_session(
        server.session_path,
        {
            "version": 1,
            "session_id": server.session_id,
            "pid": 0,
            "state": "STARTING",
        },
    )
    server.persist(force=True)
    thread = threading.Thread(target=server.serve_until_terminated, daemon=True)
    thread.start()
    return thread


def test_background_control_status_and_terminate(tmp_path):
    service = FakeService()
    session_file = tmp_path / "launcher-session.json"
    server = LauncherControlServer(
        service=service,
        session_path=session_file,
        launch_file=tmp_path / "launch.json",
        log_file=tmp_path / "launcher.log",
        session_id="test-session",
        token="test-token",
    )
    thread = _run_server(server)
    try:
        status = send_control_command(session_file, "status")
        assert status["ok"] is True
        assert status["state"] == "RUNNING"

        terminated = send_control_command(session_file, "terminate")
        assert terminated["ok"] is True
        assert terminated["state"] == "TERMINATED"
        thread.join(timeout=2)
        assert not thread.is_alive()
        assert service.terminate_calls == 1
        assert read_session(session_file)["state"] == "TERMINATED"
    finally:
        server.server_close()


def test_mismatched_session_token_cannot_terminate(tmp_path):
    service = FakeService()
    real_session = tmp_path / "real.json"
    fake_session = tmp_path / "fake.json"
    server = LauncherControlServer(
        service=service,
        session_path=real_session,
        launch_file=tmp_path / "launch.json",
        log_file=tmp_path / "launcher.log",
        session_id="real-session",
        token="real-token",
    )
    thread = _run_server(server)
    try:
        payload = read_session(real_session)
        payload["token"] = "wrong-token"
        write_session(fake_session, payload)
        with pytest.raises(LauncherControlError, match="unauthorized"):
            send_control_command(fake_session, "terminate")
        assert service.terminate_calls == 0
        assert service.state == "RUNNING"
        send_control_command(real_session, "terminate")
        thread.join(timeout=2)
    finally:
        server.server_close()


def test_stale_session_never_falls_back_to_pid_kill(tmp_path):
    session_file = tmp_path / "stale.json"
    write_session(
        session_file,
        {
            "version": 1,
            "session_id": "stale-session",
            "pid": 99999,
            "control_host": "127.0.0.1",
            "control_port": 1,
            "token": "stale",
            "launch_file": str(tmp_path / "launch.json"),
            "state": "RUNNING",
        },
    )
    with pytest.raises(LauncherControlError, match="cannot reach"):
        send_control_command(session_file, "terminate", timeout_sec=0.1)


def test_terminal_session_is_retained_for_post_run_status(tmp_path, capsys):
    from hakoniwa_pdu.apps.launcher.hako_launcher_ctl import main

    session_file = tmp_path / "terminated.json"
    write_session(
        session_file,
        {
            "version": 1,
            "pid": 1234,
            "state": "TERMINATED",
            "launch_file": str(tmp_path / "launch.json"),
        },
    )
    assert main(["status", str(session_file)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["state"] == "TERMINATED"
    assert payload["ok"] is True


def test_session_reservation_never_overwrites_existing_file(tmp_path):
    session_file = tmp_path / "launcher-session.json"
    first = {"version": 1, "session_id": "first", "state": "STARTING"}
    reserve_session(session_file, first)

    with pytest.raises(FileExistsError):
        reserve_session(
            session_file,
            {"version": 1, "session_id": "second", "state": "STARTING"},
        )

    assert read_session(session_file) == first


def test_session_preparation_lock_rejects_concurrent_owner(tmp_path):
    session_file = tmp_path / "launcher-session.json"

    with session_file_lock(session_file):
        with pytest.raises(LauncherControlError, match="another launcher"):
            with session_file_lock(session_file):
                pass


def test_live_session_is_not_overwritten(tmp_path):
    service = FakeService()
    session_file = tmp_path / "live.json"
    server = LauncherControlServer(
        service=service,
        session_path=session_file,
        launch_file=tmp_path / "launch.json",
        log_file=tmp_path / "launcher.log",
        session_id="live-session",
        token="live-token",
    )
    thread = _run_server(server)
    try:
        original = read_session(session_file)
        session_id, rc = hako_launcher._reserve_background_session(
            launch_path=tmp_path / "another-launch.json",
            session_path=session_file,
            log_path=tmp_path / "another.log",
        )
        assert session_id is None
        assert rc == 2
        assert read_session(session_file) == original
    finally:
        send_control_command(session_file, "terminate")
        thread.join(timeout=2)
        server.server_close()


def test_unreachable_session_with_live_pid_is_not_replaced(tmp_path):
    session_file = tmp_path / "ambiguous.json"
    original = {
        "version": 1,
        "session_id": "ambiguous-session",
        "pid": hako_launcher.os.getpid(),
        "control_host": "127.0.0.1",
        "control_port": 1,
        "token": "unreachable",
        "launch_file": str(tmp_path / "launch.json"),
        "state": "RUNNING",
    }
    write_session(session_file, original)

    session_id, rc = hako_launcher._reserve_background_session(
        launch_path=tmp_path / "new-launch.json",
        session_path=session_file,
        log_path=tmp_path / "new.log",
    )

    assert session_id is None
    assert rc == 2
    assert read_session(session_file) == original


def test_dead_stale_session_can_be_reused_without_killing_pid(tmp_path, monkeypatch):
    session_file = tmp_path / "stale.json"
    write_session(
        session_file,
        {
            "version": 1,
            "session_id": "old-session",
            "pid": 12345,
            "control_host": "127.0.0.1",
            "control_port": 1,
            "token": "stale",
            "launch_file": str(tmp_path / "old-launch.json"),
            "state": "RUNNING",
        },
    )
    monkeypatch.setattr(hako_launcher_control, "is_process_alive", lambda pid: False)

    session_id, rc = hako_launcher._reserve_background_session(
        launch_path=tmp_path / "new-launch.json",
        session_path=session_file,
        log_path=tmp_path / "new.log",
    )

    assert rc == 0
    assert session_id is not None
    replacement = read_session(session_file)
    assert replacement["session_id"] == session_id
    assert replacement["state"] == "STARTING"


def test_background_startup_failure_returns_nonzero_and_records_failure(
    tmp_path,
    monkeypatch,
):
    class ExitedProcess:
        pid = 4321

        def poll(self):
            return 7

    monkeypatch.setattr(
        hako_launcher.subprocess,
        "Popen",
        lambda command, **kwargs: ExitedProcess(),
    )
    session_file = tmp_path / "failed.json"

    rc = hako_launcher._spawn_background(
        str(tmp_path / "launch.json"),
        str(session_file),
    )

    assert rc == 1
    session = read_session(session_file)
    assert session["state"] == "FAILED"
    assert "rc=7" in session["error"]


def test_partial_activation_failure_cleans_up_started_assets():
    class PartialMonitor:
        def __init__(self):
            self.procs = []
            self.abort_calls = []

        def start_assets(self, timing):
            self.procs.append(object())
            raise RuntimeError("second asset failed")

        def abort(self, reason):
            self.abort_calls.append(reason)
            self.procs.clear()

    service = object.__new__(hako_launcher.LauncherService)
    service.state = "IDLE"
    service.monitor = PartialMonitor()
    service._stop_watch = threading.Event()
    service._watch_thread = None

    with pytest.raises(RuntimeError, match="second asset failed"):
        service.activate()

    assert service.monitor.abort_calls == ["terminate"]
    assert service.monitor.procs == []
    assert service.state == "TERMINATED"


def test_control_client_rejects_non_localhost_endpoint(tmp_path):
    session_file = tmp_path / "remote.json"
    write_session(
        session_file,
        {
            "version": 1,
            "session_id": "remote-session",
            "pid": 1234,
            "control_host": "192.0.2.10",
            "control_port": 8765,
            "token": "remote",
            "state": "RUNNING",
        },
    )

    with pytest.raises(LauncherControlError, match="not localhost"):
        send_control_command(session_file, "status")


def test_control_server_rejects_expected_pid_mismatch(tmp_path):
    service = FakeService()
    server = LauncherControlServer(
        service=service,
        session_path=tmp_path / "session.json",
        launch_file=tmp_path / "launch.json",
        log_file=tmp_path / "launcher.log",
        session_id="expected-session",
        token="expected-token",
    )
    try:
        response = server.dispatch(
            {
                "command": "terminate",
                "token": "expected-token",
                "session_id": "expected-session",
                "pid": hako_launcher.os.getpid() + 1,
            }
        )
        assert response["ok"] is False
        assert response["error"] == "session pid mismatch"
        assert service.terminate_calls == 0
    finally:
        server.server_close()
