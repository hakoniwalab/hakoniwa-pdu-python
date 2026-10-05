"""Windows refuses to replace or read the session file while another process
has it open (a status poll at the moment the launcher writes it). The launcher
retries those sharing violations briefly on Windows only."""

import os

import pytest

from hakoniwa_pdu.apps.launcher import hako_launcher_control as control


def _payload(state: str) -> dict[str, object]:
    return {"version": 1, "session_id": "s", "pid": os.getpid(), "state": state}


def _refuse_then(real, failures: int, calls: list):
    def action(*args):
        calls.append(args)
        if len(calls) <= failures:
            raise PermissionError(13, "Access is denied")
        return real(*args)

    return action


def test_windows_retries_a_refused_replace(tmp_path, monkeypatch):
    session = tmp_path / "launcher-session.json"
    control.write_session(session, _payload("STARTING"))
    calls: list = []
    monkeypatch.setattr(control, "_windows", lambda: True)
    monkeypatch.setattr(control, "_SHARING_RETRY_INTERVAL_SEC", 0.0)
    monkeypatch.setattr(control.os, "replace", _refuse_then(os.replace, 3, calls))
    control.write_session(session, _payload("RUNNING"))
    assert len(calls) == 4
    assert control.read_session(session)["state"] == "RUNNING"
    assert not list(tmp_path.glob(".launcher-session.json.*.tmp"))


def test_windows_gives_up_after_the_timeout(tmp_path, monkeypatch):
    session = tmp_path / "launcher-session.json"
    monkeypatch.setattr(control, "_windows", lambda: True)
    monkeypatch.setattr(control, "_SHARING_RETRY_INTERVAL_SEC", 0.0)
    monkeypatch.setattr(control, "_SHARING_RETRY_TIMEOUT_SEC", 0.0)
    monkeypatch.setattr(control.os, "replace", _refuse_then(os.replace, 10**6, []))
    with pytest.raises(PermissionError):
        control.write_session(session, _payload("RUNNING"))
    assert not list(tmp_path.glob(".launcher-session.json.*.tmp"))


def test_windows_retries_a_refused_read(tmp_path, monkeypatch):
    session = tmp_path / "launcher-session.json"
    control.write_session(session, _payload("RUNNING"))
    calls: list = []
    real = type(session).read_text
    monkeypatch.setattr(control, "_windows", lambda: True)
    monkeypatch.setattr(control, "_SHARING_RETRY_INTERVAL_SEC", 0.0)
    monkeypatch.setattr(type(session), "read_text",
                        lambda self, *args: _refuse_then(lambda *a: real(self, *a), 2, calls)(*args))
    assert control.read_session(session)["state"] == "RUNNING"
    assert len(calls) == 3


def test_posix_does_not_retry(tmp_path, monkeypatch):
    session = tmp_path / "launcher-session.json"
    calls: list = []
    monkeypatch.setattr(control, "_windows", lambda: False)
    monkeypatch.setattr(control.os, "replace", _refuse_then(os.replace, 1, calls))
    with pytest.raises(PermissionError):
        control.write_session(session, _payload("RUNNING"))
    assert len(calls) == 1


def test_other_errors_are_not_retried(tmp_path, monkeypatch):
    session = tmp_path / "launcher-session.json"
    calls: list = []

    def missing(*args):
        calls.append(args)
        raise FileNotFoundError(2, "gone")

    monkeypatch.setattr(control, "_windows", lambda: True)
    monkeypatch.setattr(control.os, "replace", missing)
    with pytest.raises(FileNotFoundError):
        control.write_session(session, _payload("RUNNING"))
    assert len(calls) == 1
