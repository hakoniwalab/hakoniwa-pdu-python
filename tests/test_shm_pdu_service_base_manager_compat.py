import os
import sys

# Add src directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from hakoniwa_pdu.impl.pdu_channel_config import PduIoInfo
from hakoniwa_pdu.rpc.shm.shm_pdu_service_base_manager import ShmPduServiceBaseManager
import hakoniwa_pdu.rpc.shm.shm_pdu_service_base_manager as base_module


class DummyConfig:
    def __init__(self, readers):
        self._readers = readers

    def get_shm_pdu_readers(self):
        return self._readers


def _make_manager_with_config(readers):
    manager = ShmPduServiceBaseManager.__new__(ShmPduServiceBaseManager)
    manager.pdu_config = DummyConfig(readers)
    return manager


def test_load_shared_memory_for_safe_uses_channel_config_reader(monkeypatch):
    calls = []

    def fake_pdu_read(robot_name, channel_id, pdu_size):
        calls.append((robot_name, channel_id, pdu_size))
        return bytearray()

    monkeypatch.setattr(base_module.hakopy, "pdu_read", fake_pdu_read)
    readers = [
        PduIoInfo("RobotA", 7, "pos", 64, "Pos"),
    ]
    manager = _make_manager_with_config(readers)
    assert manager.load_shared_memory_for_safe({"robots": []}) is True
    assert calls == [("RobotA", 7, 64)]


def test_load_shared_memory_for_safe_returns_false_without_readers(monkeypatch):
    def fake_pdu_read(_robot_name, _channel_id, _pdu_size):
        raise AssertionError("pdu_read should not be called when readers are empty")

    monkeypatch.setattr(base_module.hakopy, "pdu_read", fake_pdu_read)
    manager = _make_manager_with_config([])
    assert manager.load_shared_memory_for_safe({"robots": []}) is False
