import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from hakoniwa_pdu.impl.pdu_channel_config import PduChannelConfig
from hakoniwa_pdu.impl.communication_buffer import CommunicationBuffer
from hakoniwa_pdu.impl.data_packet import DataPacket

SAMPLE_CONFIG = {
    "robots": [
        {
            "name": "RobotA",
            "shm_pdu_readers": [
                {"org_name": "pos", "channel_id": 1, "pdu_size": 16, "type": "Pos"}
            ],
            "shm_pdu_writers": []
        }
    ]
}


def create_config_file():
    tmp = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json")
    json.dump(SAMPLE_CONFIG, tmp)
    tmp.close()
    return tmp.name


def test_put_and_get_packet():
    path = create_config_file()
    try:
        cfg = PduChannelConfig(path)
        buffer = CommunicationBuffer(cfg)
        packet = DataPacket("RobotA", 1, bytearray(b"abc"))
        buffer.put_packet(packet)
        assert buffer.contains_buffer("RobotA", "pos")
        data = buffer.get_buffer("RobotA", "pos")
        assert data == bytearray(b"abc")
        assert not buffer.contains_buffer("RobotA", "pos")
    finally:
        os.unlink(path)

