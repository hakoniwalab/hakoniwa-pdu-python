from .pdu_pytype_Int8MultiArray import Int8MultiArray
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_MultiArrayDimension import *
from ..std_msgs.pdu_cdr_conv_MultiArrayLayout import *



def py_to_cdr_body_Int8MultiArray(writer: CdrWriter, src: Int8MultiArray):
    py_to_cdr_body_MultiArrayLayout(writer, src.layout)
    writer.write_sequence_length(src.data)
    for elem in src.data:
        writer.write_int8(elem)


def cdr_body_to_py_Int8MultiArray(reader: CdrReader, dst: Int8MultiArray):
    cdr_body_to_py_MultiArrayLayout(reader, dst.layout)
    dst.data = [reader.read_int8() for _ in range(reader.read_uint32())]
    return dst


def py_to_cdr_Int8MultiArray(src: Int8MultiArray) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_Int8MultiArray(writer, src)
    return writer.bytes()


def cdr_to_py_Int8MultiArray(cdr_payload) -> Int8MultiArray:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = Int8MultiArray()
    return cdr_body_to_py_Int8MultiArray(reader, dst)
