from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Mapping


class RuntimeCleanupError(RuntimeError):
    """The Launcher cannot safely resolve or clean its Hakoniwa mmap files."""


_MMAP_FILE = re.compile(r"mmap-0x[0-9a-fA-F]+\.bin\Z")
_LOCK_FILES = frozenset({"flock.bin", "pdu_init.lock", "pro_init.lock"})


def _resolve_config_path(env: Mapping[str, str], base_dir: Path) -> Path:
    configured = env.get("HAKO_CONFIG_PATH")
    if not configured:
        raise RuntimeCleanupError(
            "runtime.cleanup_mmap_on_start requires HAKO_CONFIG_PATH"
        )
    path = Path(configured).expanduser()
    if not path.is_absolute():
        path = base_dir / path
    return path.resolve()


def _load_mmap_directory(config_path: Path) -> Path:
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeCleanupError(
            f"cannot load Hakoniwa core config: {config_path}: {exc}"
        ) from exc

    if config.get("shm_type") != "mmap":
        raise RuntimeCleanupError(
            "runtime.cleanup_mmap_on_start requires shm_type=mmap"
        )
    configured = config.get("core_mmap_path")
    if not isinstance(configured, str) or not configured.strip():
        raise RuntimeCleanupError(
            f"core_mmap_path is missing from Hakoniwa core config: {config_path}"
        )

    mmap_dir = Path(configured).expanduser()
    if not mmap_dir.is_absolute():
        mmap_dir = config_path.parent / mmap_dir
    return mmap_dir.resolve()


def cleanup_runtime_mmap(
    *,
    env: Mapping[str, str],
    base_dir: Path,
) -> list[Path]:
    """Remove only known Hakoniwa mmap/lock files from the configured directory.

    Calling this function is an explicit assertion that the Launcher exclusively
    owns the runtime directory. It deliberately does not infer ownership from a
    stored PID, because stale PIDs can be reused by unrelated processes.
    """

    config_path = _resolve_config_path(env, base_dir)
    mmap_dir = _load_mmap_directory(config_path)
    if not mmap_dir.exists():
        return []
    if not mmap_dir.is_dir():
        raise RuntimeCleanupError(f"core_mmap_path is not a directory: {mmap_dir}")

    targets = sorted(
        (
            entry
            for entry in mmap_dir.iterdir()
            if _MMAP_FILE.fullmatch(entry.name) or entry.name in _LOCK_FILES
        ),
        key=lambda entry: entry.name,
    )
    removed: list[Path] = []
    for target in targets:
        if target.is_symlink() or not target.is_file():
            raise RuntimeCleanupError(
                f"refusing to remove non-regular runtime entry: {target}"
            )
        try:
            target.unlink()
        except OSError as exc:
            raise RuntimeCleanupError(
                f"cannot remove Hakoniwa runtime file: {target}: {exc}"
            ) from exc
        removed.append(target)
    return removed
