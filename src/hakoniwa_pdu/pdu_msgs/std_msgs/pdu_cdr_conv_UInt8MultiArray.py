from .pdu_pytype_UInt8MultiArray import UInt8MultiArray
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_MultiArrayDimension import *
from ..std_msgs.pdu_cdr_conv_MultiArrayLayout import *



def py_to_cdr_body_UInt8MultiArray(writer: CdrWriter, src: UInt8MultiArray):
    py_to_cdr_body_MultiArrayLayout(writer, src.layout)
    writer.write_sequence_length(src.data)
    for elem in src.data:
        writer.write_uint8(elem)


def cdr_body_to_py_UInt8MultiArray(reader: CdrReader, dst: UInt8MultiArray):
    cdr_body_to_py_MultiArrayLayout(reader, dst.layout)
    dst.data = [reader.read_uint8() for _ in range(reader.read_uint32())]
    return dst


def py_to_cdr_UInt8MultiArray(src: UInt8MultiArray) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_UInt8MultiArray(writer, src)
    return writer.bytes()


def cdr_to_py_UInt8MultiArray(cdr_payload) -> UInt8MultiArray:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = UInt8MultiArray()
    return cdr_body_to_py_UInt8MultiArray(reader, dst)
