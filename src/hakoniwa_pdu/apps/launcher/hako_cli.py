from __future__ import annotations

import os
import sys
import shutil
import subprocess
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

    # ---- public ----
    def start(self, *, timeout: Optional[float] = None) -> int:
        return self._run("start", timeout=timeout)

    def stop(self, *, timeout: Optional[float] = None) -> int:
        return self._run("stop", timeout=timeout)

    def reset(self, *, timeout: Optional[float] = None) -> int:
        return self._run("reset", timeout=timeout)

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

    def _run(self, subcmd: Literal["start", "stop", "reset"], *, timeout: Optional[float]) -> int:
        # Only defaults.env applies here; per-asset env settings are irrelevant.
        env = merge_env(defaults_env=self.defaults_env_ops, asset_env=None, asset_name="hako_cli")

        # Resolve the command against the merged PATH.
        resolved = self._resolve_cmd(env)

        # Run in the foreground and inherit the parent stdout/stderr.
        try:
            proc = subprocess.run(
                [resolved, subcmd],
                cwd=str(self.spec.base_dir),
                env=env,
                check=False,
                timeout=timeout,
            )
            return int(proc.returncode)
        except subprocess.TimeoutExpired:
            # Return a conventional timeout exit code instead of raising.
            return 124  # Conventional exit code used by timeout on Unix-like systems.
