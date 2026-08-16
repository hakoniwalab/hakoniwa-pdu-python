import os
import sys
import threading
import time
from types import SimpleNamespace

import pytest

from hakoniwa_pdu.apps.launcher import hako_launcher
from hakoniwa_pdu.apps.launcher.hako_asset_runner import AssetRunner
from hakoniwa_pdu.apps.launcher.hako_monitor import HakoMonitor, Running


@pytest.mark.skipif(os.name != "posix", reason="POSIX process-group behavior")
def test_asset_runner_terminates_descendant_after_group_leader_exits(tmp_path):
    child_code = "import time; time.sleep(60)"
    parent_code = (
        "import subprocess, sys; "
        f"subprocess.Popen([sys.executable, '-c', {child_code!r}]); "
        "sys.exit(0)"
    )
    runner = AssetRunner()
    handle = runner.spawn(sys.executable, ["-c", parent_code], cwd=tmp_path)

    try:
        assert handle.popen.wait(timeout=5) == 0
        assert runner.is_alive(), "the descendant process group must remain managed"
        assert runner.exit_info().exited is False

        runner.terminate(grace_sec=0.2)

        assert runner.is_alive() is False
        assert runner.exit_info().exited is True
    finally:
        if runner.is_alive():
            runner.kill()


@pytest.mark.skipif(os.name != "posix", reason="POSIX process-group behavior")
def test_asset_runner_kills_descendant_that_ignores_sigterm(tmp_path):
    ready = tmp_path / "child-ready"
    child_code = (
        "import signal, sys, time; "
        "signal.signal(signal.SIGTERM, signal.SIG_IGN); "
        "open(sys.argv[1], 'w').close(); "
        "time.sleep(60)"
    )
    parent_code = (
        "import subprocess, sys; "
        f"subprocess.Popen([sys.executable, '-c', {child_code!r}, {str(ready)!r}]); "
        "sys.exit(0)"
    )
    runner = AssetRunner()
    handle = runner.spawn(sys.executable, ["-c", parent_code], cwd=tmp_path)

    try:
        assert handle.popen.wait(timeout=5) == 0
        deadline = time.time() + 5
        while not ready.exists() and time.time() < deadline:
            time.sleep(0.02)
        assert ready.exists()
        assert runner.is_alive()

        runner.terminate(grace_sec=0.1)

        assert runner.is_alive() is False
    finally:
        if runner.is_alive():
            runner.kill()


def _monitor_with(runner) -> HakoMonitor:
    monitor = object.__new__(HakoMonitor)
    monitor.procs = [
        Running(
            asset=SimpleNamespace(name="asset", start_grace_sec=0.1),
            runner=runner,
        )
    ]
    monitor._aborted = False
    monitor._cleanup_condition = threading.Condition()
    monitor._cleanup_in_progress = False
    monitor._cleanup_complete = False
    return monitor


def test_concurrent_abort_waits_for_cleanup_and_does_not_double_terminate():
    class BlockingRunner:
        def __init__(self):
            self.alive = True
            self.terminate_calls = 0
            self.kill_calls = 0
            self.entered = threading.Event()
            self.release = threading.Event()

        def is_alive(self):
            return self.alive

        def terminate(self, *, grace_sec):
            self.terminate_calls += 1
            self.entered.set()
            assert self.release.wait(timeout=2)
            self.alive = False

        def kill(self):
            self.kill_calls += 1
            self.alive = False

    runner = BlockingRunner()
    monitor = _monitor_with(runner)
    errors = []

    def abort():
        try:
            monitor.abort("test")
        except Exception as exc:  # pragma: no cover - asserted below
            errors.append(exc)

    first = threading.Thread(target=abort)
    second = threading.Thread(target=abort)
    first.start()
    assert runner.entered.wait(timeout=2)
    second.start()
    time.sleep(0.05)
    runner.release.set()
    first.join(timeout=2)
    second.join(timeout=2)

    assert not errors
    assert not first.is_alive()
    assert not second.is_alive()
    assert runner.terminate_calls == 1
    assert runner.kill_calls == 0
    assert monitor.all_terminated()


def test_terminated_service_rechecks_monitor_cleanup():
    class Monitor:
        procs = [object()]

        def __init__(self):
            self.abort_calls = []

        def abort(self, reason):
            self.abort_calls.append(reason)

    service = object.__new__(hako_launcher.LauncherService)
    service.state = "TERMINATED"
    service.monitor = Monitor()
    service._stop_watch = threading.Event()

    service.terminate()

    assert service.monitor.abort_calls == ["terminate"]
    assert service.state == "TERMINATED"


def test_cleanup_failure_does_not_report_terminated():
    class Monitor:
        procs = [object()]

        def abort(self, reason):
            raise RuntimeError("asset still alive: pid=123")

    service = object.__new__(hako_launcher.LauncherService)
    service.state = "RUNNING"
    service.monitor = Monitor()
    service._stop_watch = threading.Event()

    with pytest.raises(RuntimeError, match="asset still alive"):
        service.terminate()

    assert service.state == "FAILED"
