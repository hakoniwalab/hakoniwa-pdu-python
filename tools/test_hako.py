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
    def write_core_receipt(
        self,
        core_root: Path,
        artifact: str,
        *,
        create_artifact: bool = True,
    ) -> Path:
        receipt = (
            core_root
            / "share"
            / "hakoniwa"
            / "receipts"
            / "hakoniwa-core-pro.yaml"
        )
        receipt.parent.mkdir(parents=True, exist_ok=True)
        receipt.write_text(
            "\n".join(
                [
                    "schema_version: 1",
                    "component:",
                    "  id: hakoniwa-core-pro",
                    '  version: "1.0.0"',
                    '  source_revision: "core-revision"',
                    "build_limits:",
                    "  asset_num: 16",
                    "python:",
                    "  binding_mode: soabi",
                    '  implementation: "CPython"',
                    '  version: "3.12.10"',
                    f'  artifact: "{artifact}"',
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        artifact_path = core_root / artifact
        if create_artifact:
            artifact_path.parent.mkdir(parents=True, exist_ok=True)
            artifact_path.touch()
        return artifact_path

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
            args = HAKO.create_parser().parse_args(
                ["doctor", "--core-root", str(core)]
            )
            ctx = HAKO.Context(
                args,
                self.config(),
                HAKO.repo_root() / "hakoniwa-build.yaml",
            )
            extension = ".pyd" if ctx.os_name == "windows" else ".so"
            self.write_core_receipt(
                core,
                f"share/hakoniwa/python/hakopy{extension}",
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

    def test_hakopy_path_uses_windows_soabi_artifact_from_core_receipt(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            core = Path(temp_dir)
            args = HAKO.create_parser().parse_args(
                ["doctor", "--core-root", str(core)]
            )
            ctx = HAKO.Context(
                args,
                self.config(),
                HAKO.repo_root() / "hakoniwa-build.yaml",
            )
            ctx.os_name = "windows"
            expected = self.write_core_receipt(
                core,
                "share/hakoniwa/python/hakopy.cp312-win_amd64.pyd",
            )

            self.assertEqual(HAKO._hakopy_path(ctx), expected.resolve())

    def test_hakopy_path_accepts_posix_soabi_artifact_from_core_receipt(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            core = Path(temp_dir)
            args = HAKO.create_parser().parse_args(
                ["doctor", "--core-root", str(core)]
            )
            ctx = HAKO.Context(
                args,
                self.config(),
                HAKO.repo_root() / "hakoniwa-build.yaml",
            )
            ctx.os_name = "linux"
            expected = self.write_core_receipt(
                core,
                "share/hakoniwa/python/hakopy.cpython-312-x86_64-linux-gnu.so",
            )

            self.assertEqual(HAKO._hakopy_path(ctx), expected.resolve())

    def test_hakopy_path_rejects_artifact_outside_core_prefix(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            core = Path(temp_dir) / "core"
            args = HAKO.create_parser().parse_args(
                ["doctor", "--core-root", str(core)]
            )
            ctx = HAKO.Context(
                args,
                self.config(),
                HAKO.repo_root() / "hakoniwa-build.yaml",
            )
            ctx.os_name = "windows"
            self.write_core_receipt(
                core,
                "../hakopy.cp312-win_amd64.pyd",
                create_artifact=False,
            )

            with self.assertRaisesRegex(HAKO.HakoError, "escapes the Core prefix"):
                HAKO._hakopy_path(ctx)

    def test_hakopy_path_rejects_non_hakopy_extension(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            core = Path(temp_dir)
            args = HAKO.create_parser().parse_args(
                ["doctor", "--core-root", str(core)]
            )
            ctx = HAKO.Context(
                args,
                self.config(),
                HAKO.repo_root() / "hakoniwa-build.yaml",
            )
            ctx.os_name = "windows"
            self.write_core_receipt(
                core,
                "share/hakoniwa/python/hakopy-helper.cp312-win_amd64.pyd",
            )

            with self.assertRaisesRegex(HAKO.HakoError, "not a hakopy extension"):
                HAKO._hakopy_path(ctx)

    def test_hakopy_path_uses_unambiguous_legacy_artifact(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            core = Path(temp_dir)
            suffix = HAKO.EXTENSION_SUFFIXES[0]
            artifact = f"share/hakoniwa/python/hakopy{suffix}"
            expected = core / artifact
            self.write_core_receipt(
                core,
                artifact,
            )
            receipt = (
                core
                / "share"
                / "hakoniwa"
                / "receipts"
                / "hakoniwa-core-pro.yaml"
            )
            receipt.write_text(
                receipt.read_text(encoding="utf-8").replace(
                    f'  artifact: "{artifact}"\n',
                    "",
                ),
                encoding="utf-8",
            )
            args = HAKO.create_parser().parse_args(
                ["doctor", "--core-root", str(core)]
            )
            ctx = HAKO.Context(
                args,
                self.config(),
                HAKO.repo_root() / "hakoniwa-build.yaml",
            )
            ctx.os_name = "windows" if suffix.endswith(".pyd") else "macos"

            self.assertEqual(HAKO._hakopy_path(ctx), expected.resolve())

    def test_hakopy_path_rejects_ambiguous_legacy_artifacts(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            core = Path(temp_dir)
            first = "share/hakoniwa/python/hakopy.cp312-win_amd64.pyd"
            second = core / "share/hakoniwa/python/hakopy.pyd"
            self.write_core_receipt(core, first)
            second.touch()
            receipt = (
                core
                / "share"
                / "hakoniwa"
                / "receipts"
                / "hakoniwa-core-pro.yaml"
            )
            receipt.write_text(
                receipt.read_text(encoding="utf-8").replace(
                    f'  artifact: "{first}"\n',
                    "",
                ),
                encoding="utf-8",
            )
            args = HAKO.create_parser().parse_args(
                ["doctor", "--core-root", str(core)]
            )
            ctx = HAKO.Context(
                args,
                self.config(),
                HAKO.repo_root() / "hakoniwa-build.yaml",
            )
            ctx.os_name = "windows"

            with patch.object(
                HAKO,
                "EXTENSION_SUFFIXES",
                [".cp312-win_amd64.pyd", ".pyd"],
            ), self.assertRaisesRegex(HAKO.HakoError, "not unique"):
                HAKO._hakopy_path(ctx)

    def test_doctor_reports_missing_receipt_declared_artifact(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            core = Path(temp_dir)
            args = HAKO.create_parser().parse_args(
                ["doctor", "--core-root", str(core)]
            )
            ctx = HAKO.Context(
                args,
                self.config(),
                HAKO.repo_root() / "hakoniwa-build.yaml",
            )
            ctx.os_name = "windows"
            self.write_core_receipt(
                core,
                "share/hakoniwa/python/hakopy.cp312-win_amd64.pyd",
                create_artifact=False,
            )

            with patch.object(HAKO.subprocess, "run") as run:
                run.return_value = HAKO.subprocess.CompletedProcess(
                    args=[], returncode=0
                )
                errors = HAKO.doctor(ctx)

            self.assertEqual(len(errors), 1)
            self.assertIn("Receipt-declared hakopy artifact not found", errors[0])

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

    def test_build_removes_stale_distribution_wheels(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            args = HAKO.create_parser().parse_args(
                ["build", "--build-dir", temp_dir]
            )
            ctx = HAKO.Context(
                args,
                self.config(),
                HAKO.repo_root() / "hakoniwa-build.yaml",
            )
            stale = ctx.build_dir / "hakoniwa_pdu-1.6.3-py3-none-any.whl"
            stale.parent.mkdir(parents=True, exist_ok=True)
            stale.touch()

            with patch.object(HAKO, "_run"):
                HAKO.build(ctx)

            self.assertFalse(stale.exists())

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
            hakopy = (
                prefix
                / "share"
                / "hakoniwa"
                / "python"
                / "hakopy.cpython-312-test.so"
            )

            with patch.object(Path, "is_file", return_value=True), patch.object(
                HAKO, "_wheel", return_value=wheel
            ), patch.object(HAKO, "_run") as run, patch.object(
                HAKO, "_site_packages", return_value=ctx.venv_dir
            ), patch.object(
                HAKO,
                "_require_hakopy",
                return_value=hakopy,
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
            self.assertEqual(
                (ctx.venv_dir / "hakoniwa_foundation_core.pth").read_text(
                    encoding="utf-8"
                ),
                str(hakopy.parent) + "\n",
            )

    def test_receipt_declares_launcher_background_lifecycle(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            args = HAKO.create_parser().parse_args(
                [
                    "install",
                    "--install-dir",
                    temp_dir,
                    "--core-root",
                    temp_dir,
                ]
            )
            ctx = HAKO.Context(
                args,
                self.config(),
                HAKO.repo_root() / "hakoniwa-build.yaml",
            )
            dependency = {
                "version": "1.0.0",
                "source_revision": "core-revision",
                "build_limits": {
                    "asset_num": 16,
                },
            }
            with patch.object(HAKO.shutil, "copyfile"), patch.object(
                HAKO, "_read_core_receipt", return_value=dependency
            ), patch.object(
                HAKO, "_command_output", return_value="pdu-python-revision"
            ):
                receipt = HAKO.write_receipt(
                    ctx,
                    {
                        "Name": "hakoniwa-pdu",
                        "Version": "1.6.4",
                        "Location": str(ctx.venv_dir),
                    },
                )

            content = receipt.read_text(encoding="utf-8")
            self.assertIn("launcher_background_lifecycle: true", content)


if __name__ == "__main__":
    unittest.main()
