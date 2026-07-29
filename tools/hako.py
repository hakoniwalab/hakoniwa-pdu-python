#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Mapping


DEFAULT_MANIFEST = "hakoniwa-build.yaml"


class HakoError(RuntimeError):
    pass


class ConfigError(HakoError):
    pass


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _parse_scalar(text: str) -> Any:
    value = text.strip()
    if value == "":
        return {}
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if value.startswith(('"', "'")) and len(value) >= 2 and value[-1] == value[0]:
        return value[1:-1]
    try:
        return int(value)
    except ValueError:
        return value


def load_simple_yaml(path: Path) -> Dict[str, Any]:
    root: Dict[str, Any] = {}
    stack: list[tuple[int, Dict[str, Any]]] = [(-1, root)]
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        stripped = line.lstrip(" ")
        indent = len(line) - len(stripped)
        if ":" not in stripped or stripped.startswith("-"):
            raise ConfigError(f"{path}:{lineno}: expected 'key: value'")
        key, value = stripped.split(":", 1)
        while stack and indent <= stack[-1][0]:
            stack.pop()
        if not stack:
            raise ConfigError(f"{path}:{lineno}: invalid indentation")
        parent = stack[-1][1]
        if key in parent:
            raise ConfigError(f"{path}:{lineno}: duplicate key: {key}")
        parsed = _parse_scalar(value)
        parent[key] = parsed
        if isinstance(parsed, dict):
            stack.append((indent, parsed))
    return root


def _exact_keys(value: Mapping[str, Any], expected: set[str], location: str) -> None:
    unknown = sorted(set(value) - expected)
    missing = sorted(expected - set(value))
    if unknown:
        raise ConfigError(f"unknown key(s) under {location}: {', '.join(unknown)}")
    if missing:
        raise ConfigError(f"missing required key(s) under {location}: {', '.join(missing)}")


def resolve_config(raw: Mapping[str, Any]) -> Dict[str, Any]:
    _exact_keys(raw, {"version", "build", "paths"}, "root")
    if raw["version"] != 1:
        raise ConfigError("version must be 1")
    if not isinstance(raw["build"], Mapping):
        raise ConfigError("build must be a mapping")
    if not isinstance(raw["paths"], Mapping):
        raise ConfigError("paths must be a mapping")
    _exact_keys(raw["build"], {"dir", "install_dir"}, "build")
    _exact_keys(raw["paths"], {"hakoniwa_core_root"}, "paths")
    for key in ("dir", "install_dir"):
        if not isinstance(raw["build"][key], str) or not raw["build"][key]:
            raise ConfigError(f"build.{key} must be a non-empty string")
    if not isinstance(raw["paths"]["hakoniwa_core_root"], str):
        raise ConfigError("paths.hakoniwa_core_root must be a string")
    return {
        "version": 1,
        "build": dict(raw["build"]),
        "paths": dict(raw["paths"]),
    }


def manifest_path(value: str | None) -> Path:
    if value is None:
        path = repo_root() / DEFAULT_MANIFEST
    else:
        path = Path(value)
        if not path.is_absolute():
            path = Path.cwd() / path
        path = path.resolve()
    if not path.is_file():
        raise ConfigError(f"build manifest not found: {path}")
    return path


def _path(value: str, base: Path) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = base / path
    return path.resolve()


class Context:
    def __init__(
        self,
        args: argparse.Namespace,
        cfg: Mapping[str, Any],
        manifest: Path,
    ) -> None:
        self.root = repo_root()
        self.manifest = manifest
        self.build_dir = _path(args.build_dir or cfg["build"]["dir"], self.root)
        self.install_dir = _path(
            args.install_dir or cfg["build"]["install_dir"],
            self.root,
        )
        core_value = args.core_root or cfg["paths"]["hakoniwa_core_root"]
        self.core_root = _path(core_value, self.root) if core_value else None
        system = platform.system()
        self.os_name = {
            "Darwin": "macos",
            "Linux": "linux",
            "Windows": "windows",
        }.get(system, system.lower())
        machine = platform.machine().lower()
        self.arch = {
            "x86_64": "x64",
            "amd64": "x64",
            "aarch64": "arm64",
        }.get(machine, machine)

    @property
    def venv_dir(self) -> Path:
        return self.install_dir / "python"

    @property
    def venv_python(self) -> Path:
        if self.os_name == "windows":
            return self.venv_dir / "Scripts" / "python.exe"
        return self.venv_dir / "bin" / "python"


def _run(command: list[str], cwd: Path) -> None:
    print(">", subprocess.list2cmdline(command))
    subprocess.run(command, cwd=cwd, check=True)


def doctor(ctx: Context) -> list[str]:
    errors: list[str] = []
    if sys.version_info < (3, 12):
        errors.append("Python 3.12 or newer is required")
    for module in ("pip",):
        result = subprocess.run(
            [sys.executable, "-c", f"import {module}"],
            check=False,
            capture_output=True,
        )
        if result.returncode:
            errors.append(f"Python build prerequisite is missing: {module}")
    hakopy = (
        ctx.core_root / "share" / "hakoniwa" / "python" / "hakopy.so"
        if ctx.core_root
        else None
    )
    if hakopy is None or not hakopy.is_file():
        errors.append(
            "Foundation Core hakopy is required; set paths.hakoniwa_core_root "
            "or --core-root"
        )
    return errors


def _yaml_scalar(value: Any) -> str:
    if isinstance(value, int):
        return str(value)
    return json.dumps(str(value), ensure_ascii=False)


def write_resolved(ctx: Context, operation: str) -> Path:
    path = ctx.root / ".hako" / "resolved-build.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "version: 1",
                f"manifest: {_yaml_scalar(ctx.manifest)}",
                f"operation: {_yaml_scalar(operation)}",
                "platform:",
                f"  os: {_yaml_scalar(ctx.os_name)}",
                f"  architecture: {_yaml_scalar(ctx.arch)}",
                f"  python: {_yaml_scalar(platform.python_version())}",
                "build:",
                f"  dir: {_yaml_scalar(ctx.build_dir)}",
                f"  install_dir: {_yaml_scalar(ctx.install_dir)}",
                f"  venv_dir: {_yaml_scalar(ctx.venv_dir)}",
                "resolved_paths:",
                f"  hakoniwa_core_root: {_yaml_scalar(ctx.core_root or '')}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def build(ctx: Context) -> None:
    ctx.build_dir.mkdir(parents=True, exist_ok=True)
    _run(
        [
            sys.executable,
            "-m",
            "pip",
            "wheel",
            "--no-deps",
            "--wheel-dir",
            str(ctx.build_dir),
            str(ctx.root),
        ],
        ctx.root,
    )


def _wheel(ctx: Context) -> Path:
    wheels = sorted(ctx.build_dir.glob("hakoniwa_pdu-*.whl"))
    if len(wheels) != 1:
        raise HakoError(
            f"expected one hakoniwa_pdu wheel under {ctx.build_dir}; "
            "run hako.py build first"
        )
    return wheels[0]


def _site_packages(ctx: Context) -> Path:
    result = subprocess.run(
        [
            str(ctx.venv_python),
            "-c",
            "import site; print(site.getsitepackages()[0])",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return Path(result.stdout.strip()).resolve()


def pip_show(ctx: Context) -> Dict[str, str]:
    result = subprocess.run(
        [str(ctx.venv_python), "-m", "pip", "show", "hakoniwa-pdu"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        raise HakoError("Foundation venv does not contain hakoniwa-pdu")
    metadata: Dict[str, str] = {}
    for line in result.stdout.splitlines():
        if ": " in line:
            key, value = line.split(": ", 1)
            metadata[key] = value
    for key in ("Name", "Version", "Location"):
        if not metadata.get(key):
            raise HakoError(f"pip show output is missing {key}")
    location = Path(metadata["Location"]).resolve()
    try:
        location.relative_to(ctx.venv_dir.resolve())
    except ValueError as exc:
        raise HakoError(
            f"pip show resolved a non-Foundation installation: {location}"
        ) from exc
    return metadata


def _read_core_receipt(ctx: Context) -> Dict[str, Any]:
    if ctx.core_root is None:
        raise HakoError("Foundation Core root is not resolved")
    path = (
        ctx.core_root
        / "share"
        / "hakoniwa"
        / "receipts"
        / "hakoniwa-core-pro.yaml"
    )
    if not path.is_file():
        raise HakoError(f"Core Component Receipt not found: {path}")
    result: Dict[str, Any] = {"build_limits": {}}
    section = ""
    for raw in path.read_text(encoding="utf-8").splitlines():
        if raw and not raw.startswith(" ") and raw.endswith(":"):
            section = raw[:-1]
            continue
        if not raw.startswith("  ") or raw.startswith("    ") or ":" not in raw:
            continue
        key, value = raw.strip().split(":", 1)
        parsed = _parse_scalar(value)
        if section == "component" and key in {"version", "source_revision"}:
            result[key] = parsed
        elif section == "build_limits":
            result["build_limits"][key] = parsed
    return result


def _command_output(command: list[str], cwd: Path) -> str:
    result = subprocess.run(
        command,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def write_receipt(ctx: Context, package: Mapping[str, str]) -> Path:
    receipt_root = ctx.install_dir / "share" / "hakoniwa" / "receipts"
    resolved_relative = (
        Path("share")
        / "hakoniwa"
        / "receipts"
        / "resolved"
        / "hakoniwa-pdu-python.yaml"
    )
    (ctx.install_dir / resolved_relative).parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(
        ctx.root / ".hako" / "resolved-build.yaml",
        ctx.install_dir / resolved_relative,
    )
    dependency = _read_core_receipt(ctx)
    limits = dependency["build_limits"]
    revision = _command_output(["git", "rev-parse", "HEAD"], ctx.root)
    lines = [
        "schema_version: 1",
        "component:",
        "  id: hakoniwa-pdu-python",
        f"  version: {_yaml_scalar(package['Version'])}",
        f"  source_revision: {_yaml_scalar(revision)}",
        "platform:",
        f"  os: {_yaml_scalar(ctx.os_name)}",
        f"  architecture: {_yaml_scalar(ctx.arch)}",
        f"  toolchain: {_yaml_scalar(ctx.venv_python)}",
        "install:",
        f"  prefix: {_yaml_scalar(ctx.install_dir)}",
        "capabilities:",
        "  hako_launcher: true",
        "  shm_backend: true",
        "  external_rpc: true",
        "  websocket: true",
        "build_limits:",
    ]
    for key, value in limits.items():
        lines.append(f"  {key}: {value}")
    lines.extend(
        [
            "dependencies:",
            "  hakoniwa-core-pro:",
            f"    version: {_yaml_scalar(dependency['version'])}",
            f"    source_revision: {_yaml_scalar(dependency['source_revision'])}",
            "    build_limits:",
        ]
    )
    for key, value in limits.items():
        lines.append(f"      {key}: {value}")
    lines.extend(
        [
            "artifacts:",
            '  - path: "python"',
            "    kind: python-venv",
            f"resolved_manifest: {_yaml_scalar(resolved_relative.as_posix())}",
        ]
    )
    receipt_path = receipt_root / "hakoniwa-pdu-python.yaml"
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return receipt_path


def install(ctx: Context) -> None:
    wheel = _wheel(ctx)
    if not ctx.venv_python.is_file():
        _run([sys.executable, "-m", "venv", str(ctx.venv_dir)], ctx.root)
    _run(
        [
            str(ctx.venv_python),
            "-m",
            "pip",
            "install",
            "--upgrade",
            "setuptools",
            "cffi",
            str(wheel),
        ],
        ctx.root,
    )
    _run(
        [
            str(ctx.venv_python),
            "-m",
            "pip",
            "install",
            "--force-reinstall",
            "--no-deps",
            str(wheel),
        ],
        ctx.root,
    )
    if ctx.core_root is None:
        raise HakoError("Foundation Core root is not resolved")
    core_python = ctx.core_root / "share" / "hakoniwa" / "python"
    (_site_packages(ctx) / "hakoniwa_foundation_core.pth").write_text(
        str(core_python) + "\n",
        encoding="utf-8",
    )
    package = pip_show(ctx)
    _smoke_import(ctx)
    print(
        f"Foundation pip show: {package['Name']} {package['Version']} "
        f"({package['Location']})"
    )
    receipt = write_receipt(ctx, package)
    print(f"Component Receipt: {receipt}")


def _smoke_import(ctx: Context) -> None:
    _run(
        [
            str(ctx.venv_python),
            "-c",
            (
                "import hakopy; "
                "import hakoniwa_pdu.apps.launcher.hako_launcher; "
                "import hakoniwa_pdu.impl.shm_communication_service"
            ),
        ],
        ctx.root,
    )


def smoke(ctx: Context) -> None:
    package = pip_show(ctx)
    _smoke_import(ctx)
    print(
        f"Foundation PDU Python smoke passed: {package['Name']} "
        f"{package['Version']} ({package['Location']})"
    )


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Hakoniwa PDU Python build driver")
    parser.add_argument(
        "command",
        choices=["doctor", "configure", "build", "install", "smoke"],
    )
    parser.add_argument("--config", default=None)
    parser.add_argument("--build-dir", default=None)
    parser.add_argument("--install-dir", default=None)
    parser.add_argument("--core-root", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = create_parser().parse_args(argv)
    manifest = manifest_path(args.config)
    cfg = resolve_config(load_simple_yaml(manifest))
    ctx = Context(args, cfg, manifest)
    errors = doctor(ctx)
    print(
        f"Hakoniwa PDU Python: {ctx.os_name}-{ctx.arch}, "
        f"Python {platform.python_version()}"
    )
    print(f"Build directory: {ctx.build_dir}")
    print(f"Install prefix : {ctx.install_dir}")
    print(f"Foundation venv: {ctx.venv_dir}")
    print(f"Core root      : {ctx.core_root or 'not resolved'}")
    resolved = write_resolved(ctx, args.command)
    print(f"Resolved configuration: {resolved}")
    if args.command == "doctor":
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1 if errors else 0
    if errors:
        raise HakoError("doctor found blocking prerequisites: " + "; ".join(errors))
    if args.command == "build":
        build(ctx)
    elif args.command == "install":
        install(ctx)
    elif args.command == "smoke":
        smoke(ctx)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (HakoError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
