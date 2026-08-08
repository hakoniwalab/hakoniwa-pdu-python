import os
import threading

import pytest

from hakoniwa_pdu.apps.launcher import hako_launcher_control as control


class FakeService:
    def __init__(self) -> None:
        self.state = "RUNNING"

    def status(self) -> str:
        return self.state

    def terminate(self) -> None:
        self.state = "TERMINATED"


def _starting_payload(session_id: str) -> dict[str, object]:
    return {
        "version": 1,
        "session_id": session_id,
        "pid": os.getpid(),
        "state": "STARTING",
    }


def test_claim_session_probes_owner_without_holding_preparation_lock(
    tmp_path,
    monkeypatch,
):
    session_file = tmp_path / "live.json"
    existing = {
        "version": 1,
        "session_id": "live-session",
        "pid": os.getpid(),
        "control_host": "127.0.0.1",
        "control_port": 12345,
        "token": "live-token",
        "state": "RUNNING",
    }
    control.write_session(session_file, existing)
    probe_acquired_lock = False

    def probe_owner(*args, **kwargs):
        nonlocal probe_acquired_lock
        with control.session_file_lock(session_file):
            probe_acquired_lock = True
        return {"ok": True, "state": "RUNNING"}

    monkeypatch.setattr(control, "send_control_command", probe_owner)

    with pytest.raises(control.LauncherSessionConflict, match="already active"):
        control.claim_session(
            session_file,
            _starting_payload("new-session"),
        )

    assert probe_acquired_lock is True
    assert control.read_session(session_file) == existing


def test_control_server_retries_persist_while_preparation_lock_is_held(
    tmp_path,
    monkeypatch,
):
    service = FakeService()
    session_file = tmp_path / "live.json"
    server = control.LauncherControlServer(
        service=service,
        session_path=session_file,
        launch_file=tmp_path / "launch.json",
        log_file=tmp_path / "launcher.log",
        session_id="live-session",
        token="live-token",
    )
    control.reserve_session(session_file, _starting_payload(server.session_id))
    server.persist(force=True)

    persist_attempted = threading.Event()
    original_write_owned_session = control.write_owned_session

    def observed_write_owned_session(*args, **kwargs):
        persist_attempted.set()
        return original_write_owned_session(*args, **kwargs)

    monkeypatch.setattr(
        control,
        "write_owned_session",
        observed_write_owned_session,
    )

    with control.session_file_lock(session_file):
        thread = threading.Thread(
            target=server.serve_until_terminated,
            daemon=True,
        )
        thread.start()
        assert persist_attempted.wait(timeout=1.0)
        thread.join(timeout=0.05)
        assert thread.is_alive()

    try:
        status = control.send_control_command(session_file, "status")
        assert status["state"] == "RUNNING"
        control.send_control_command(session_file, "terminate")
        thread.join(timeout=2.0)
        assert not thread.is_alive()
    finally:
        server.server_close()


def test_claim_session_does_not_replace_changed_owner(tmp_path, monkeypatch):
    session_file = tmp_path / "session.json"
    existing = {
        "version": 1,
        "session_id": "old-session",
        "pid": 12345,
        "control_host": "127.0.0.1",
        "control_port": 1,
        "token": "stale",
        "state": "RUNNING",
    }
    replacement = {
        **existing,
        "session_id": "replacement-session",
        "pid": os.getpid(),
    }
    control.write_session(session_file, existing)

    def replace_during_probe(*args, **kwargs):
        control.write_session(session_file, replacement)
        raise control.LauncherControlError("cannot reach")

    monkeypatch.setattr(control, "send_control_command", replace_during_probe)
    monkeypatch.setattr(control, "is_process_alive", lambda pid: False)

    with pytest.raises(
        control.LauncherSessionConflict,
        match="changed while validating",
    ):
        control.claim_session(
            session_file,
            _starting_payload("new-session"),
        )

    assert control.read_session(session_file) == replacement
