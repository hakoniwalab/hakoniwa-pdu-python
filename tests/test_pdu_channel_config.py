import json
import os
import sys
import tempfile

# Add src directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from hakoniwa_pdu.impl.pdu_channel_config import PduChannelConfig

SAMPLE_CONFIG = {
    "robots": [
        {
            "name": "RobotA",
            "shm_pdu_readers": [
                {"org_name": "pos", "channel_id": 1, "pdu_size": 16, "type": "Pos"}
            ],
            "shm_pdu_writers": [
                {"org_name": "cmd", "channel_id": 2, "pdu_size": 8, "type": "Cmd"}
            ]
        }
    ]
}

SAMPLE_PDUTYPES = [
    {"name": "pos", "channel_id": 1, "pdu_size": 16, "type": "Pos"},
    {"name": "cmd", "channel_id": 2, "pdu_size": 8, "type": "Cmd"},
]

SAMPLE_COMPACT_PDUEF = {
    "paths": [
        {"id": "default", "path": "pdutypes.json"}
    ],
    "robots": [
        {"name": "RobotA", "pdutypes_id": "default"}
    ]
}


def create_config_file():
    tmp = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json")
    json.dump(SAMPLE_CONFIG, tmp)
    tmp.close()
    return tmp.name

def create_compact_config_files():
    tmp_dir = tempfile.mkdtemp(prefix="pdudef_compact_")
    pdutypes_path = os.path.join(tmp_dir, "pdutypes.json")
    pdudef_path = os.path.join(tmp_dir, "pdudef.json")
    with open(pdutypes_path, "w", encoding="utf-8") as f:
        json.dump(SAMPLE_PDUTYPES, f)
    with open(pdudef_path, "w", encoding="utf-8") as f:
        json.dump(SAMPLE_COMPACT_PDUEF, f)
    return tmp_dir, pdudef_path


def test_pdu_channel_config_queries():
    path = create_config_file()
    try:
        cfg = PduChannelConfig(path)
        assert cfg.get_pdu_name("RobotA", 1) == "pos"
        assert cfg.get_pdu_name("RobotA", 2) == "cmd"
        assert cfg.get_pdu_name("RobotA", 999) is None

        assert cfg.get_pdu_size("RobotA", "pos") == 16
        assert cfg.get_pdu_size("RobotA", "unknown") == -1

        assert cfg.get_pdu_type("RobotA", "cmd") == "Cmd"
        assert cfg.get_pdu_type("RobotA", "missing") is None

        assert cfg.get_pdu_channel_id("RobotA", "cmd") == 2
        assert cfg.get_pdu_channel_id("RobotA", "missing") == -1
    finally:
        os.unlink(path)


def test_pdu_channel_config_compact_queries():
    tmp_dir, path = create_compact_config_files()
    try:
        cfg = PduChannelConfig(path)
        assert cfg.get_pdu_name("RobotA", 1) == "pos"
        assert cfg.get_pdu_name("RobotA", 2) == "cmd"
        assert cfg.get_pdu_name("RobotA", 999) is None

        assert cfg.get_pdu_size("RobotA", "pos") == 16
        assert cfg.get_pdu_size("RobotA", "unknown") == -1

        assert cfg.get_pdu_type("RobotA", "cmd") == "Cmd"
        assert cfg.get_pdu_type("RobotA", "missing") is None

        assert cfg.get_pdu_channel_id("RobotA", "cmd") == 2
        assert cfg.get_pdu_channel_id("RobotA", "missing") == -1
    finally:
        os.unlink(path)
        os.unlink(os.path.join(tmp_dir, "pdutypes.json"))
        os.rmdir(tmp_dir)


def test_get_pdudef_keeps_legacy_compatible_view_for_compact_input():
    tmp_dir, path = create_compact_config_files()
    try:
        cfg = PduChannelConfig(path)
        pdudef = cfg.get_pdudef()
        assert "robots" in pdudef
        assert len(pdudef["robots"]) == 1
        robot = pdudef["robots"][0]
        assert robot["name"] == "RobotA"
        assert len(robot["shm_pdu_readers"]) == 2
        assert len(robot["shm_pdu_writers"]) == 2
        assert robot["shm_pdu_readers"][0]["org_name"] == "pos"
        assert robot["shm_pdu_writers"][1]["org_name"] == "cmd"
    finally:
        os.unlink(path)
        os.unlink(os.path.join(tmp_dir, "pdutypes.json"))
        os.rmdir(tmp_dir)


def test_get_pdudef_compact_from_compact_input():
    tmp_dir, path = create_compact_config_files()
    try:
        cfg = PduChannelConfig(path)
        compact = cfg.get_pdudef_compact()
        assert "robots" in compact
        assert len(compact["robots"]) == 1
        robot = compact["robots"][0]
        assert robot["name"] == "RobotA"
        assert len(robot["pdus"]) == 2
        assert robot["pdus"][0]["name"] == "pos"
        assert robot["pdus"][0]["channel_id"] == 1
        assert robot["pdus"][1]["name"] == "cmd"
        assert robot["pdus"][1]["channel_id"] == 2
    finally:
        os.unlink(path)
        os.unlink(os.path.join(tmp_dir, "pdutypes.json"))
        os.rmdir(tmp_dir)


def test_get_pdudef_compact_from_legacy_input():
    path = create_config_file()
    try:
        cfg = PduChannelConfig(path)
        compact = cfg.get_pdudef_compact()
        assert "robots" in compact
        assert len(compact["robots"]) == 1
        robot = compact["robots"][0]
        assert robot["name"] == "RobotA"
        assert len(robot["pdus"]) == 2
        names = {pdu["name"] for pdu in robot["pdus"]}
        assert names == {"pos", "cmd"}
    finally:
        os.unlink(path)
