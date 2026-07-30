import json
import threading

import pytest

from hakoniwa_pdu.apps.launcher.hako_launcher_background import (
    LauncherControlError,
    LauncherControlServer,
    read_session,
    send_control_command,
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
