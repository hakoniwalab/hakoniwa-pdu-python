import json
import os
import sys
import tempfile

# Add src directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from hakoniwa_pdu.rpc import service_config as rpc_service_config_module
from hakoniwa_pdu.service import hako_asset_service_config as asset_service_config_module


class DummyOffmap:
    def get_pdu_size(self, pdu_type: str) -> int:
        if pdu_type.endswith("RequestPacket"):
            return 100
        if pdu_type.endswith("ResponsePacket"):
            return 200
        raise KeyError(pdu_type)


def _create_service_json() -> str:
    data = {
        "pduMetaDataSize": 4,
        "services": [
            {
                "name": "SvcA",
                "type": "Pos",
                "maxClients": 1,
                "pduSize": {
                    "server": {"heapSize": 3},
                    "client": {"heapSize": 5},
                },
            }
        ],
        "nodes": [
            {
                "name": "RobotA",
                "topics": [
                    {"topic_name": "pos", "type": "Pos", "pduSize": {"heapSize": 0}},
                    {"topic_name": "cmd", "type": "Pos", "pduSize": {"heapSize": 0}},
                ],
            }
        ],
    }
    fd, path = tempfile.mkstemp(prefix="svc_patch_", suffix=".json")
    os.close(fd)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)
    return path


def _assert_patched(path: str):
    with open(path, "r", encoding="utf-8") as f:
        patched = json.load(f)
    service = patched["services"][0]
    assert service["pduSize"]["server"]["baseSize"] == 100
    assert service["pduSize"]["client"]["baseSize"] == 200
    topics = patched["nodes"][0]["topics"]
    assert topics[0]["channel_id"] == 0
    assert topics[1]["channel_id"] == 1


def test_rpc_patch_service_base_size(monkeypatch):
    path = _create_service_json()
    try:
        monkeypatch.setattr(rpc_service_config_module.offset_map, "create_offmap", lambda _: DummyOffmap())
        rpc_service_config_module.patch_service_base_size(path, "dummy_offset_dir")
        _assert_patched(path)
    finally:
        os.unlink(path)


def test_asset_patch_service_base_size(monkeypatch):
    path = _create_service_json()
    try:
        monkeypatch.setattr(asset_service_config_module, "create_offmap", lambda _: DummyOffmap())
        asset_service_config_module.patch_service_base_size(path, "dummy_offset_dir")
        _assert_patched(path)
    finally:
        os.unlink(path)
