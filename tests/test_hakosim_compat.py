import json
import os
import sys
import tempfile

# Add src directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from hakoniwa_pdu.apps.drone.hakosim import MultirotorClient


LEGACY_PDUEF = {
    "robots": [
        {
            "name": "DroneA",
            "rpc_pdu_readers": [],
            "rpc_pdu_writers": [],
            "shm_pdu_readers": [
                {"org_name": "pos", "channel_id": 1, "pdu_size": 16, "type": "Pos"}
            ],
            "shm_pdu_writers": [
                {"org_name": "cmd", "channel_id": 2, "pdu_size": 8, "type": "Cmd"}
            ],
        }
    ]
}

COMPACT_PDUTYPES = [
    {"name": "pos", "channel_id": 1, "pdu_size": 16, "type": "Pos"},
    {"name": "cmd", "channel_id": 2, "pdu_size": 8, "type": "Cmd"},
]

COMPACT_PDUEF = {
    "paths": [{"id": "default", "path": "pdutypes.json"}],
    "robots": [{"name": "DroneA", "pdutypes_id": "default"}],
}


def _create_legacy_file():
    fd, path = tempfile.mkstemp(prefix="legacy_pdudef_", suffix=".json")
    os.close(fd)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(LEGACY_PDUEF, f)
    return path


def _create_compact_files():
    tmp_dir = tempfile.mkdtemp(prefix="compact_pdudef_")
    pdutypes_path = os.path.join(tmp_dir, "pdutypes.json")
    pdudef_path = os.path.join(tmp_dir, "pdudef.json")
    with open(pdutypes_path, "w", encoding="utf-8") as f:
        json.dump(COMPACT_PDUTYPES, f)
    with open(pdudef_path, "w", encoding="utf-8") as f:
        json.dump(COMPACT_PDUEF, f)
    return tmp_dir, pdudef_path


def test_multirotor_client_accepts_legacy_pdudef():
    path = _create_legacy_file()
    try:
        client = MultirotorClient(path)
        assert client.default_drone_name == "DroneA"
        assert "DroneA" in client.vehicles
    finally:
        os.unlink(path)


def test_multirotor_client_accepts_compact_pdudef():
    tmp_dir, path = _create_compact_files()
    try:
        client = MultirotorClient(path)
        assert client.default_drone_name == "DroneA"
        assert "DroneA" in client.vehicles
    finally:
        os.unlink(path)
        os.unlink(os.path.join(tmp_dir, "pdutypes.json"))
        os.rmdir(tmp_dir)
