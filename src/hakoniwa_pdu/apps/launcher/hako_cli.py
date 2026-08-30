from __future__ import annotations

import os
import sys
import shutil
import subprocess
import re
from typing import Optional, Literal

from .effective_model import EffectiveSpec
from .envmerge import merge_env


class HakoCli:
    """
    Thin wrapper to run hako-cmd in the foreground.
    - Resolve PATH after merging defaults.env into the OS environment
    - Run from the launch.json directory (base_dir)
    - Inherit the parent process stdout/stderr without capturing output
    """

    def __init__(
        self,
        spec: EffectiveSpec,
        *,
        defaults_env_ops: Optional[dict] = None,
        cmd: str = "hako-cmd",
    ) -> None:
        self.spec = spec
        self.defaults_env_ops = defaults_env_ops  # PATH/lib_path are merged here.
        self.cmd = cmd
        self._bounded_lock_wait_supported: Optional[bool] = None
        self._detected_version: Optional[tuple[int, int, int]] = None

    def prepare(self) -> tuple[Optional[tuple[int, int, int]], bool]:
        """Resolve and inspect hako-cmd once before Launcher operations."""
        env = merge_env(
            defaults_env=self.defaults_env_ops,
            asset_env=None,
            asset_name="hako_cli",
        )
        resolved = self._resolve_cmd(env)
        supported = self._supports_bounded_lock_wait(resolved, env)
        return self._detected_version, supported

    # ---- public ----
    def start(self, *, timeout: Optional[float] = None) -> int:
        return self._run("start", timeout=timeout)

    def stop(self, *, timeout: Optional[float] = None) -> int:
        return self._run("stop", timeout=timeout)

    def reset(self, *, timeout: Optional[float] = None) -> int:
        return self._run("reset", timeout=timeout)

    def list_assets(self, *, timeout: Optional[float] = None) -> tuple[int, set[str]]:
        """Return registered Hakoniwa asset names without leaking probe output."""
        env = merge_env(
            defaults_env=self.defaults_env_ops,
            asset_env=None,
            asset_name="hako_cli",
        )
        resolved = self._resolve_cmd(env)
        command = self._command(resolved, "ls", timeout=timeout, env=env)
        try:
            proc = subprocess.run(
                command,
                cwd=str(self.spec.base_dir),
                env=env,
                check=False,
                timeout=timeout,
                capture_output=True,
                text=True,
            )
        except subprocess.TimeoutExpired:
            return 124, set()
        names = {
            line.strip()
            for line in proc.stdout.splitlines()
            if line.strip()
        }
        return int(proc.returncode), names

    # ---- internals ----
    def _resolve_cmd(self, env: dict[str, str]) -> str:
        path = env.get("PATH")
        candidates = [self.cmd]
        # On WSL/Linux, bare command names do not auto-resolve to .exe.
        if os.name != "nt" and not self.cmd.lower().endswith(".exe"):
            candidates.append(f"{self.cmd}.exe")

        for candidate in candidates:
            resolved = shutil.which(candidate, path=path)
            if resolved is not None:
                return resolved

        raise FileNotFoundError(
            f"'{self.cmd}' was not found. Check PATH "
            f"(current PATH head: { (path or '').split(os.pathsep)[0] if path else '<empty>' })"
        )

    def _supports_bounded_lock_wait(self, resolved: str, env: dict[str, str]) -> bool:
        if self._bounded_lock_wait_supported is not None:
            return self._bounded_lock_wait_supported
        try:
            proc = subprocess.run(
                [resolved, "--version"],
                cwd=str(self.spec.base_dir),
                env=env,
                check=False,
                timeout=1.0,
                capture_output=True,
                text=True,
            )
        except (OSError, subprocess.TimeoutExpired):
            self._bounded_lock_wait_supported = False
            return False

        match = re.search(r"^hako-cmd version (\d+)\.(\d+)\.(\d+)$", proc.stdout, re.MULTILINE)
        if proc.returncode == 0 and match is not None:
            self._detected_version = tuple(int(value) for value in match.groups())
        self._bounded_lock_wait_supported = bool(
            self._detected_version is not None
            and self._detected_version >= (1, 0, 1)
        )
        return self._bounded_lock_wait_supported

    def _command(
        self,
        resolved: str,
        subcmd: Literal["start", "stop", "reset", "ls"],
        *,
        timeout: Optional[float],
        env: dict[str, str],
    ) -> list[str]:
        command = [resolved, subcmd]
        if not self._supports_bounded_lock_wait(resolved, env):
            return command

        # Keep the native lock wait inside the Python subprocess watchdog.
        # Lifecycle commands without an outer timeout use hako-cmd's 3 s default.
        lock_timeout_ms = 3000
        if timeout is not None:
            lock_timeout_ms = max(1, int(timeout * 1000 * 0.8))
        command.extend(["--lock-timeout-ms", str(lock_timeout_ms)])
        return command

    def _run(self, subcmd: Literal["start", "stop", "reset"], *, timeout: Optional[float]) -> int:
        # Only defaults.env applies here; per-asset env settings are irrelevant.
        env = merge_env(defaults_env=self.defaults_env_ops, asset_env=None, asset_name="hako_cli")

        # Resolve the command against the merged PATH.
        resolved = self._resolve_cmd(env)
        command = self._command(resolved, subcmd, timeout=timeout, env=env)

        # Run in the foreground and inherit the parent stdout/stderr.
        try:
            proc = subprocess.run(
                command,
                cwd=str(self.spec.base_dir),
                env=env,
                check=False,
                timeout=timeout,
            )
            return int(proc.returncode)
        except subprocess.TimeoutExpired:
            # Return a conventional timeout exit code instead of raising.
            return 124  # Conventional exit code used by timeout on Unix-like systems.
