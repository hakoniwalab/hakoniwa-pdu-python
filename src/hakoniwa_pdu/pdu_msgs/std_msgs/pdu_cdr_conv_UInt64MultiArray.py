from .pdu_pytype_UInt64MultiArray import UInt64MultiArray
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_MultiArrayDimension import *
from ..std_msgs.pdu_cdr_conv_MultiArrayLayout import *



def py_to_cdr_body_UInt64MultiArray(writer: CdrWriter, src: UInt64MultiArray):
    py_to_cdr_body_MultiArrayLayout(writer, src.layout)
    writer.write_sequence_length(src.data)
    for elem in src.data:
        writer.write_uint64(elem)


def cdr_body_to_py_UInt64MultiArray(reader: CdrReader, dst: UInt64MultiArray):
    cdr_body_to_py_MultiArrayLayout(reader, dst.layout)
    dst.data = [reader.read_uint64() for _ in range(reader.read_uint32())]
    return dst


def py_to_cdr_UInt64MultiArray(src: UInt64MultiArray) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_UInt64MultiArray(writer, src)
    return writer.bytes()


def cdr_to_py_UInt64MultiArray(cdr_payload) -> UInt64MultiArray:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = UInt64MultiArray()
    return cdr_body_to_py_UInt64MultiArray(reader, dst)
