import json
import os
import sys
import tempfile

# Add src directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from hakoniwa_pdu.rpc.service_config import ServiceConfig as RpcServiceConfig
from hakoniwa_pdu.service.hako_asset_service_config import (
    HakoAssetServiceConfig as AssetServiceConfig,
)
import hakoniwa_pdu.service.hako_asset_service_config as asset_cfg_module


class DummyOffmap:
    def get_pdu_size(self, pdu_type: str) -> int:
        if pdu_type in ("Pos", "PosRequestPacket", "PosResponsePacket"):
            return 16
        raise KeyError(pdu_type)


class DummyHakopy:
    def __init__(self):
        self.created = []

    def asset_service_get_channel_id(self, service_id: int, client_id: int):
        return (service_id * 100 + client_id * 2, service_id * 100 + client_id * 2 + 1)

    def pdu_create(self, robot_name: str, channel_id: int, pdu_size: int):
        self.created.append((robot_name, channel_id, pdu_size))
        return True


def _create_service_config_file() -> str:
    config = {
        "pduMetaDataSize": 4,
        "services": [],
        "nodes": [
            {
                "name": "RobotA",
                "topics": [
                    {
                        "topic_name": "pos",
                        "type": "Pos",
                        "channel_id": 1,
                        "pduSize": {"heapSize": 0},
                    }
                ],
            }
        ],
    }
    fd, path = tempfile.mkstemp(prefix="service_cfg_", suffix=".json")
    os.close(fd)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f)
    return path

def _create_service_with_rpc_config_file() -> str:
    config = {
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
        "nodes": [],
    }
    fd, path = tempfile.mkstemp(prefix="service_rpc_cfg_", suffix=".json")
    os.close(fd)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f)
    return path


def _compact_base() -> dict:
    return {
        "paths": [{"id": "default", "path": "pdutypes.json"}],
        "robots": [{"name": "RobotA", "pdutypes_id": "default"}],
    }


def _legacy_base() -> dict:
    return {
        "robots": [
            {
                "name": "RobotA",
                "rpc_pdu_readers": [],
                "rpc_pdu_writers": [],
                "shm_pdu_readers": [],
                "shm_pdu_writers": [],
            }
        ]
    }


def _assert_robot_a_has_pos_pdu(result: dict):
    robot = next(r for r in result["robots"] if r["name"] == "RobotA")
    assert len(robot.get("shm_pdu_readers", [])) == 1
    assert len(robot.get("shm_pdu_writers", [])) == 1
    assert robot["shm_pdu_readers"][0]["org_name"] == "pos"
    assert robot["shm_pdu_readers"][0]["channel_id"] == 1
    assert robot["shm_pdu_readers"][0]["pdu_size"] == 20


def test_rpc_service_config_append_accepts_legacy_and_compact():
    path = _create_service_config_file()
    try:
        cfg = RpcServiceConfig(path, DummyOffmap(), hakopy=None)
        legacy_result = cfg.append_pdu_def(_legacy_base())
        _assert_robot_a_has_pos_pdu(legacy_result)

        compact_result = cfg.append_pdu_def(_compact_base())
        _assert_robot_a_has_pos_pdu(compact_result)
        robot = next(r for r in compact_result["robots"] if r["name"] == "RobotA")
        assert robot["pdutypes_id"] == "default"
    finally:
        os.unlink(path)


def test_asset_service_config_append_accepts_legacy_and_compact():
    path = _create_service_config_file()
    try:
        cfg = AssetServiceConfig(path, DummyOffmap())
        legacy_result = cfg.append_pdu_def(_legacy_base())
        _assert_robot_a_has_pos_pdu(legacy_result)

        compact_result = cfg.append_pdu_def(_compact_base())
        _assert_robot_a_has_pos_pdu(compact_result)
        robot = next(r for r in compact_result["robots"] if r["name"] == "RobotA")
        assert robot["pdutypes_id"] == "default"
    finally:
        os.unlink(path)


def test_rpc_service_config_generates_service_req_res_channels():
    path = _create_service_with_rpc_config_file()
    try:
        cfg = RpcServiceConfig(path, DummyOffmap(), hakopy=None)
        result = cfg.append_pdu_def(None)
        robot = next(r for r in result["robots"] if r["name"] == "SvcA")
        assert len(robot["shm_pdu_readers"]) == 1
        assert len(robot["shm_pdu_writers"]) == 1

        req = robot["shm_pdu_readers"][0]
        res = robot["shm_pdu_writers"][0]
        assert req["org_name"] == "req_0"
        assert req["name"] == "SvcA_req_0"
        assert req["channel_id"] == -1
        assert req["pdu_size"] == 23  # 4(meta) + 16(base) + 3(heap)

        assert res["org_name"] == "res_0"
        assert res["name"] == "SvcA_res_0"
        assert res["channel_id"] == -1
        assert res["pdu_size"] == 25  # 4(meta) + 16(base) + 5(heap)
    finally:
        os.unlink(path)


def test_asset_service_config_generates_service_req_res_channels(monkeypatch):
    path = _create_service_with_rpc_config_file()
    try:
        monkeypatch.setattr(
            asset_cfg_module.hakopy,
            "asset_service_get_channel_id",
            lambda service_id, client_id: (10, 11),
        )
        cfg = AssetServiceConfig(path, DummyOffmap())
        result = cfg.append_pdu_def(None)
        robot = next(r for r in result["robots"] if r["name"] == "SvcA")
        assert len(robot["shm_pdu_readers"]) == 1
        assert len(robot["shm_pdu_writers"]) == 1

        req = robot["shm_pdu_readers"][0]
        res = robot["shm_pdu_writers"][0]
        assert req["org_name"] == "req_0"
        assert req["channel_id"] == 10
        assert req["pdu_size"] == 23
        assert res["org_name"] == "res_0"
        assert res["channel_id"] == 11
        assert res["pdu_size"] == 25
    finally:
        os.unlink(path)


def test_rpc_service_config_get_pdu_name_and_create_pdus_compact_internal():
    path = _create_service_with_rpc_config_file()
    try:
        hakopy = DummyHakopy()
        cfg = RpcServiceConfig(path, DummyOffmap(), hakopy=hakopy)
        assert cfg.get_pdu_name("SvcA", 0) == "req_0"
        robots = cfg.create_pdus()
        assert robots["robots"][0]["name"] == "SvcA"
        assert ("SvcA", 0, 23) in hakopy.created
        assert ("SvcA", 1, 25) in hakopy.created
    finally:
        os.unlink(path)


def test_asset_service_config_get_pdu_name_and_create_pdus_compact_internal(monkeypatch):
    path = _create_service_with_rpc_config_file()
    try:
        monkeypatch.setattr(
            asset_cfg_module.hakopy,
            "asset_service_get_channel_id",
            lambda service_id, client_id: (10, 11),
        )
        created = []
        monkeypatch.setattr(
            asset_cfg_module.hakopy,
            "pdu_create",
            lambda robot_name, channel_id, pdu_size: created.append((robot_name, channel_id, pdu_size)) or True,
        )
        cfg = AssetServiceConfig(path, DummyOffmap())
        assert cfg.get_pdu_name("SvcA", 10) == "req_0"
        robots = cfg.create_pdus()
        assert robots["robots"][0]["name"] == "SvcA"
        assert ("SvcA", 10, 23) in created
        assert ("SvcA", 11, 25) in created
    finally:
        os.unlink(path)
