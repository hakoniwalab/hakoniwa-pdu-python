import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from hakoniwa_pdu.impl.data_packet import DataPacket


def test_decode_too_short():
    # less than minimum 12 bytes
    result = DataPacket.decode(bytearray(b'\x00\x01'))
    assert result is None


def test_decode_invalid_length():
    # header indicates name_len longer than actual data
    data = bytearray()
    data.extend((8).to_bytes(4, 'little'))  # header len
    data.extend((5).to_bytes(4, 'little'))  # name len
    data.extend(b'ab')  # name bytes incomplete
    data.extend((1).to_bytes(4, 'little'))  # channel_id
    # no body data
    result = DataPacket.decode(data)
    assert result is None

