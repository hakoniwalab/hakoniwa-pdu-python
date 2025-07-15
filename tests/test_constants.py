import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from hakoniwa_pdu.impl.data_packet import (
    DECLARE_PDU_FOR_READ,
    DECLARE_PDU_FOR_WRITE,
    REQUEST_PDU_READ,
)


def test_magic_numbers():
    assert DECLARE_PDU_FOR_READ == 0x52455044
    assert DECLARE_PDU_FOR_WRITE == 0x57505044
    assert REQUEST_PDU_READ == 0x57505045
