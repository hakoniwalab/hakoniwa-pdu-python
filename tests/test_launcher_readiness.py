import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from hakoniwa_pdu.apps.launcher.hako_cli import HakoCli
from hakoniwa_pdu.apps.launcher.hako_monitor import HakoMonitor
from hakoniwa_pdu.apps.launcher.model import Asset


class LauncherReadinessTest(unittest.TestCase):
    def test_hako_asset_readiness_is_optional(self):
        asset = Asset(name="http-server", command="python3")
        self.assertIsNone(asset.readiness)

    def test_hako_asset_readiness_defaults_are_materialized(self):
        asset = Asset(
            name="drone-service-1",
            command="drone-service",
            readiness={"type": "hako_asset", "asset_name": "drone-1"},
        )
        self.assertIsNotNone(asset.readiness)
        self.assertEqual(asset.readiness.asset_name, "drone-1")
        self.assertEqual(asset.readiness.timeout_sec, 30.0)
        self.assertEqual(asset.readiness.poll_interval_sec, 0.2)
        self.assertEqual(asset.readiness.command_timeout_sec, 1.0)

    def test_hako_cli_list_assets_captures_exact_lines(self):
        with tempfile.TemporaryDirectory() as temporary:
            cli = HakoCli(SimpleNamespace(base_dir=Path(temporary)))
            cli._resolve_cmd = lambda env: "/test/hako-cmd"
            version = SimpleNamespace(
                returncode=0,
                stdout="hako-cmd version 1.0.1\n",
            )
            completed = SimpleNamespace(
                returncode=0,
                stdout="drone-1\nShowRunnerAsset\n",
            )
            with mock.patch.object(
                subprocess, "run", side_effect=[version, completed]
            ) as run:
                rc, names = cli.list_assets(timeout=0.5)

            self.assertEqual(rc, 0)
            self.assertEqual(names, {"drone-1", "ShowRunnerAsset"})
            self.assertEqual(run.call_count, 2)
            self.assertEqual(run.call_args_list[0].args[0], ["/test/hako-cmd", "--version"])
            self.assertEqual(
                run.call_args.args[0],
                ["/test/hako-cmd", "ls", "--lock-timeout-ms", "400"],
            )
            self.assertTrue(run.call_args.kwargs["capture_output"])
            self.assertEqual(run.call_args.kwargs["timeout"], 0.5)

    def test_hako_cli_uses_legacy_command_for_old_version(self):
        with tempfile.TemporaryDirectory() as temporary:
            cli = HakoCli(SimpleNamespace(base_dir=Path(temporary)))
            cli._resolve_cmd = lambda env: "/test/hako-cmd"
            version = SimpleNamespace(
                returncode=0,
                stdout="hako-cmd version 1.0.0\n",
            )
            completed = SimpleNamespace(returncode=0, stdout="drone-1\n")
            with mock.patch.object(
                subprocess, "run", side_effect=[version, completed]
            ) as run:
                rc, names = cli.list_assets(timeout=0.5)

            self.assertEqual((rc, names), (0, {"drone-1"}))
            self.assertEqual(run.call_args.args[0], ["/test/hako-cmd", "ls"])

    def test_hako_cli_list_assets_bounds_a_hung_probe(self):
        with tempfile.TemporaryDirectory() as temporary:
            cli = HakoCli(SimpleNamespace(base_dir=Path(temporary)))
            cli._resolve_cmd = lambda env: "/test/hako-cmd"
            with mock.patch.object(
                subprocess,
                "run",
                side_effect=subprocess.TimeoutExpired("hako-cmd", 0.1),
            ):
                self.assertEqual(cli.list_assets(timeout=0.1), (124, set()))

    def test_monitor_waits_until_expected_hako_asset_is_listed(self):
        class Provider:
            def __init__(self):
                self.calls = 0

            def list_assets(self, *, timeout=None):
                self.calls += 1
                names = {"drone-1"} if self.calls >= 2 else set()
                return 0, names

        with tempfile.TemporaryDirectory() as temporary:
            provider = Provider()
            monitor = HakoMonitor(
                SimpleNamespace(
                    base_dir=Path(temporary),
                    assets=[],
                    notify=None,
                ),
                asset_list_provider=provider,
            )
            asset = SimpleNamespace(
                name="drone-service-1",
                readiness={
                    "type": "hako_asset",
                    "asset_name": "drone-1",
                    "timeout_sec": 0.2,
                    "poll_interval_sec": 0.001,
                    "command_timeout_sec": 0.01,
                },
            )
            self.assertTrue(monitor._wait_readiness(asset))
            self.assertEqual(provider.calls, 2)

    def test_monitor_readiness_wait_is_bounded(self):
        class Provider:
            def __init__(self):
                self.calls = 0

            def list_assets(self, *, timeout=None):
                self.calls += 1
                return 0, set()

        with tempfile.TemporaryDirectory() as temporary:
            provider = Provider()
            monitor = HakoMonitor(
                SimpleNamespace(
                    base_dir=Path(temporary),
                    assets=[],
                    notify=None,
                ),
                asset_list_provider=provider,
            )
            asset = SimpleNamespace(
                name="drone-service-1",
                readiness={
                    "type": "hako_asset",
                    "asset_name": "drone-1",
                    "timeout_sec": 0.005,
                    "poll_interval_sec": 0.001,
                    "command_timeout_sec": 0.002,
                },
            )

            self.assertFalse(monitor._wait_readiness(asset))
            self.assertGreater(provider.calls, 0)

    def test_readiness_timeout_aborts_started_asset(self):
        class Provider:
            def list_assets(self, *, timeout=None):
                return 0, set()

        class Runner:
            def __init__(self, *, env=None):
                self.alive = False
                self.terminated = False

            def spawn(self, *args, **kwargs):
                self.alive = True

            def is_alive(self):
                return self.alive

            def terminate(self, *, grace_sec):
                self.terminated = True
                self.alive = False

            def kill(self):
                self.alive = False

        with tempfile.TemporaryDirectory() as temporary:
            asset = SimpleNamespace(
                name="drone-service-1",
                command="drone-service",
                args=[],
                cwd=Path(temporary),
                stdout=None,
                stderr=None,
                env=None,
                activation_timing="before_start",
                start_grace_sec=0.0,
                delay_sec=0.0,
                readiness={
                    "type": "hako_asset",
                    "asset_name": "drone-1",
                    "timeout_sec": 0.005,
                    "poll_interval_sec": 0.001,
                    "command_timeout_sec": 0.002,
                },
            )
            monitor = HakoMonitor(
                SimpleNamespace(
                    base_dir=Path(temporary),
                    assets=[asset],
                    notify=None,
                ),
                asset_list_provider=Provider(),
            )
            runner = Runner()
            with mock.patch(
                "hakoniwa_pdu.apps.launcher.hako_monitor.AssetRunner",
                return_value=runner,
            ):
                with self.assertRaisesRegex(
                    RuntimeError,
                    "asset readiness timed out",
                ):
                    monitor.start_assets("before_start")

            self.assertTrue(runner.terminated)
            self.assertTrue(monitor.all_terminated())


if __name__ == "__main__":
    unittest.main()
