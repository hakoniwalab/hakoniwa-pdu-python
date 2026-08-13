import pytest

from hakoniwa_pdu.impl.hako_binary import binary_io as legacy_binary_io
from hakoniwa_pdu.pdu_msgs import binary_io
from hakoniwa_pdu.pdu_msgs.std_msgs.pdu_conv_ByteMultiArray import (
    pdu_to_py_ByteMultiArray,
    py_to_pdu_ByteMultiArray,
)
from hakoniwa_pdu.pdu_msgs.std_msgs.pdu_conv_Char import (
    pdu_to_py_Char,
    py_to_pdu_Char,
)
from hakoniwa_pdu.pdu_msgs.std_msgs.pdu_pytype_ByteMultiArray import ByteMultiArray
from hakoniwa_pdu.pdu_msgs.std_msgs.pdu_pytype_Char import Char


@pytest.mark.parametrize("runtime", [binary_io, legacy_binary_io])
@pytest.mark.parametrize("type_name", ["byte", "char"])
def test_byte_and_char_are_uint8_in_all_native_runtime_paths(runtime, type_name):
    encoded = runtime.typeTobin(type_name, 255)
    assert encoded == b"\xff"
    assert runtime.binTovalue(type_name, encoded) == 255

    encoded_array = runtime.typeTobin_array(type_name, [0, 127, 255])
    assert list(runtime.binToArrayValues(type_name, encoded_array)) == [0, 127, 255]


def test_generated_char_roundtrip_uses_an_integer():
    value = Char()
    value.data = 254

    restored = pdu_to_py_Char(py_to_pdu_Char(value))

    assert restored.data == 254
    assert Char.__annotations__["data"] is int


def test_byte_multi_array_roundtrip_accepts_full_uint8_range():
    value = ByteMultiArray()
    value.data = [0, 127, 255]

    restored = pdu_to_py_ByteMultiArray(py_to_pdu_ByteMultiArray(value))

    assert list(restored.data) == value.data
