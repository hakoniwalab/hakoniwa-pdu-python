import os
import sys
import struct

# Add src directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from hakoniwa_pdu.impl.data_packet import DataPacket, HAKO_META_MAGIC, HAKO_META_VER


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


def test_decode_v2_endpoint_raw_frame():
    robot = b"Drone" + b"\x00" * (128 - 5)
    meta = bytearray(176)
    struct.pack_into("<I", meta, 0, HAKO_META_MAGIC)
    struct.pack_into("<H", meta, 4, HAKO_META_VER)
    struct.pack_into("<H", meta, 6, 0)
    struct.pack_into("<I", meta, 8, 0)
    struct.pack_into("<I", meta, 12, 0x42555043)
    struct.pack_into("<I", meta, 16, 172 + 3)
    struct.pack_into("<I", meta, 20, 3)
    struct.pack_into("<Q", meta, 24, 1)
    struct.pack_into("<Q", meta, 32, 2)
    struct.pack_into("<Q", meta, 40, 3)
    struct.pack_into("<i", meta, 48, 7)
    frame = robot + bytes(meta) + b"abc"

    decoded = DataPacket.decode(bytearray(frame), version="v2")
    assert decoded is not None
    assert decoded.get_robot_name() == "Drone"
    assert decoded.get_channel_id() == 7
    assert decoded.get_pdu_data() == bytearray(b"abc")


def test_encode_decode_v2_roundtrip():
    packet = DataPacket("Drone2", 9, bytearray(b"xyz"))
    encoded = packet.encode(version="v2", meta_request_type=0x42555043)
    decoded = DataPacket.decode(encoded, version="v2")

    assert decoded is not None
    assert len(encoded) == 304 + 3
    assert decoded.get_robot_name() == "Drone2"
    assert decoded.get_channel_id() == 9
    assert decoded.get_pdu_data() == bytearray(b"xyz")
