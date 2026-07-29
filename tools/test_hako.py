from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).with_name("hako.py")
SPEC = importlib.util.spec_from_file_location("hako_pdu_python_tool", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
HAKO = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = HAKO
SPEC.loader.exec_module(HAKO)


class ManifestTests(unittest.TestCase):
    def config(self):
        return HAKO.resolve_config(
            HAKO.load_simple_yaml(HAKO.repo_root() / "hakoniwa-build.yaml")
        )

    def test_repository_manifest_is_valid(self):
        self.assertEqual(self.config()["version"], 1)

    def test_default_manifest_is_repository_relative(self):
        self.assertEqual(
            HAKO.manifest_path(None),
            HAKO.repo_root() / "hakoniwa-build.yaml",
        )

    def test_venv_is_inside_install_prefix(self):
        args = HAKO.create_parser().parse_args(["doctor"])
        ctx = HAKO.Context(
            args,
            self.config(),
            HAKO.repo_root() / "hakoniwa-build.yaml",
        )
        self.assertEqual(ctx.venv_dir, ctx.install_dir / "python")

    def test_pip_show_rejects_non_foundation_location(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            args = HAKO.create_parser().parse_args(
                ["smoke", "--install-dir", temp_dir]
            )
            ctx = HAKO.Context(
                args,
                self.config(),
                HAKO.repo_root() / "hakoniwa-build.yaml",
            )
            completed = HAKO.subprocess.CompletedProcess(
                args=[],
                returncode=0,
                stdout=(
                    "Name: hakoniwa-pdu\n"
                    "Version: 1.6.3\n"
                    "Location: /usr/local/lib/python3.12/site-packages\n"
                ),
                stderr="",
            )
            with patch.object(HAKO.subprocess, "run", return_value=completed):
                with self.assertRaisesRegex(HAKO.HakoError, "non-Foundation"):
                    HAKO.pip_show(ctx)

    def test_doctor_does_not_require_host_setuptools(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            core = Path(temp_dir)
            hakopy = core / "share" / "hakoniwa" / "python" / "hakopy.so"
            hakopy.parent.mkdir(parents=True)
            hakopy.touch()
            args = HAKO.create_parser().parse_args(
                ["doctor", "--core-root", str(core)]
            )
            ctx = HAKO.Context(
                args,
                self.config(),
                HAKO.repo_root() / "hakoniwa-build.yaml",
            )

            with patch.object(HAKO.subprocess, "run") as run:
                run.return_value = HAKO.subprocess.CompletedProcess(
                    args=[], returncode=0
                )
                errors = HAKO.doctor(ctx)

            self.assertEqual(errors, [])
            commands = [call.args[0] for call in run.call_args_list]
            self.assertEqual(
                commands,
                [[sys.executable, "-c", "import pip"]],
            )

    def test_build_uses_pep517_isolation(self):
        args = HAKO.create_parser().parse_args(["build"])
        ctx = HAKO.Context(
            args,
            self.config(),
            HAKO.repo_root() / "hakoniwa-build.yaml",
        )

        with patch.object(HAKO, "_run") as run:
            HAKO.build(ctx)

        command = run.call_args.args[0]
        self.assertNotIn("--no-build-isolation", command)
        self.assertEqual(command[:4], [sys.executable, "-m", "pip", "wheel"])

    def test_install_force_reinstalls_same_version_wheel_before_receipt(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            prefix = Path(temp_dir)
            args = HAKO.create_parser().parse_args(
                [
                    "install",
                    "--install-dir",
                    str(prefix),
                    "--core-root",
                    str(prefix),
                ]
            )
            ctx = HAKO.Context(
                args,
                self.config(),
                HAKO.repo_root() / "hakoniwa-build.yaml",
            )
            ctx.venv_dir.mkdir(parents=True)
            wheel = ctx.build_dir / "hakoniwa_pdu-1.6.3-py3-none-any.whl"

            with patch.object(Path, "is_file", return_value=True), patch.object(
                HAKO, "_wheel", return_value=wheel
            ), patch.object(HAKO, "_run") as run, patch.object(
                HAKO, "_site_packages", return_value=ctx.venv_dir
            ), patch.object(
                HAKO, "pip_show", return_value={
                    "Name": "hakoniwa-pdu",
                    "Version": "1.6.3",
                    "Location": str(ctx.venv_dir),
                }
            ), patch.object(
                HAKO, "_smoke_import"
            ), patch.object(
                HAKO, "write_receipt", return_value=Path("receipt.yaml")
            ):
                HAKO.install(ctx)

            commands = [call.args[0] for call in run.call_args_list]
            self.assertIn(
                [
                    str(ctx.venv_python),
                    "-m",
                    "pip",
                    "install",
                    "--force-reinstall",
                    "--no-deps",
                    str(wheel),
                ],
                commands,
            )


if __name__ == "__main__":
    unittest.main()
