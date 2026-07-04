from .pdu_pytype_UInt32MultiArray import UInt32MultiArray
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_MultiArrayDimension import *
from ..std_msgs.pdu_cdr_conv_MultiArrayLayout import *



def py_to_cdr_body_UInt32MultiArray(writer: CdrWriter, src: UInt32MultiArray):
    py_to_cdr_body_MultiArrayLayout(writer, src.layout)
    writer.write_sequence_length(src.data)
    for elem in src.data:
        writer.write_uint32(elem)


def cdr_body_to_py_UInt32MultiArray(reader: CdrReader, dst: UInt32MultiArray):
    cdr_body_to_py_MultiArrayLayout(reader, dst.layout)
    dst.data = [reader.read_uint32() for _ in range(reader.read_uint32())]
    return dst


def py_to_cdr_UInt32MultiArray(src: UInt32MultiArray) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_UInt32MultiArray(writer, src)
    return writer.bytes()


def cdr_to_py_UInt32MultiArray(cdr_payload) -> UInt32MultiArray:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = UInt32MultiArray()
    return cdr_body_to_py_UInt32MultiArray(reader, dst)
