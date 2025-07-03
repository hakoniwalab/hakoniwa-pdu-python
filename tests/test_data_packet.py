import os
import sys

# Add src directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from hakoniwa_pdu.impl.data_packet import DataPacket


def test_encode_decode_roundtrip():
    robot_name = 'RobotA'
    channel_id = 42
    body = bytearray(b'\x01\x02\x03')

    packet = DataPacket(robot_name, channel_id, body)
    encoded = packet.encode()

    decoded = DataPacket.decode(encoded)
    assert decoded is not None

    assert decoded.get_robot_name() == robot_name
    assert decoded.get_channel_id() == channel_id
    assert decoded.get_pdu_data() == body
