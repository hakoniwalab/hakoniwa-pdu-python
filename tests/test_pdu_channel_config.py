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


def create_config_file():
    tmp = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json")
    json.dump(SAMPLE_CONFIG, tmp)
    tmp.close()
    return tmp.name


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

