import json

import pytest

from hakoniwa_pdu.apps.launcher.hako_runtime_cleanup import (
    RuntimeCleanupError,
    cleanup_runtime_mmap,
)
from hakoniwa_pdu.apps.launcher.model import LauncherSpec


def _write_core_config(tmp_path, mmap_dir):
    config = tmp_path / "cpp_core_config.json"
    config.write_text(
        json.dumps({"shm_type": "mmap", "core_mmap_path": str(mmap_dir)}),
        encoding="utf-8",
    )
    return config


def test_runtime_cleanup_is_opt_in():
    spec = LauncherSpec(assets=[{"name": "asset", "command": "asset"}])
    assert spec.runtime is None

    enabled = LauncherSpec(
        runtime={"cleanup_mmap_on_start": True},
        assets=[{"name": "asset", "command": "asset"}],
    )
    assert enabled.runtime is not None
    assert enabled.runtime.cleanup_mmap_on_start is True


def test_cleanup_removes_only_managed_runtime_files(tmp_path):
    mmap_dir = tmp_path / "mmap"
    mmap_dir.mkdir()
    managed_names = {
        "mmap-0xff.bin",
        "mmap-0x100.bin",
        "mmap-0x101.bin",
        "flock.bin",
        "pdu_init.lock",
        "pro_init.lock",
    }
    for name in managed_names:
        (mmap_dir / name).write_bytes(b"stale")
    unrelated = mmap_dir / "operator-notes.txt"
    unrelated.write_text("keep", encoding="utf-8")
    config = _write_core_config(tmp_path, mmap_dir)

    removed = cleanup_runtime_mmap(
        env={"HAKO_CONFIG_PATH": str(config)},
        base_dir=tmp_path,
    )

    assert {path.name for path in removed} == managed_names
    assert unrelated.read_text(encoding="utf-8") == "keep"


def test_cleanup_requires_explicit_core_config(tmp_path):
    with pytest.raises(RuntimeCleanupError, match="requires HAKO_CONFIG_PATH"):
        cleanup_runtime_mmap(env={}, base_dir=tmp_path)


def test_cleanup_rejects_non_mmap_configuration(tmp_path):
    config = tmp_path / "cpp_core_config.json"
    config.write_text(json.dumps({"shm_type": "sem"}), encoding="utf-8")

    with pytest.raises(RuntimeCleanupError, match="requires shm_type=mmap"):
        cleanup_runtime_mmap(
            env={"HAKO_CONFIG_PATH": str(config)},
            base_dir=tmp_path,
        )
