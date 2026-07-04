from .pdu_pytype_UInt16MultiArray import UInt16MultiArray
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_MultiArrayDimension import *
from ..std_msgs.pdu_cdr_conv_MultiArrayLayout import *



def py_to_cdr_body_UInt16MultiArray(writer: CdrWriter, src: UInt16MultiArray):
    py_to_cdr_body_MultiArrayLayout(writer, src.layout)
    writer.write_sequence_length(src.data)
    for elem in src.data:
        writer.write_uint16(elem)


def cdr_body_to_py_UInt16MultiArray(reader: CdrReader, dst: UInt16MultiArray):
    cdr_body_to_py_MultiArrayLayout(reader, dst.layout)
    dst.data = [reader.read_uint16() for _ in range(reader.read_uint32())]
    return dst


def py_to_cdr_UInt16MultiArray(src: UInt16MultiArray) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_UInt16MultiArray(writer, src)
    return writer.bytes()


def cdr_to_py_UInt16MultiArray(cdr_payload) -> UInt16MultiArray:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = UInt16MultiArray()
    return cdr_body_to_py_UInt16MultiArray(reader, dst)
