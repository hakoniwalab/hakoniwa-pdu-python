from .pdu_pytype_Int64MultiArray import Int64MultiArray
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_MultiArrayDimension import *
from ..std_msgs.pdu_cdr_conv_MultiArrayLayout import *



def py_to_cdr_body_Int64MultiArray(writer: CdrWriter, src: Int64MultiArray):
    py_to_cdr_body_MultiArrayLayout(writer, src.layout)
    writer.write_sequence_length(src.data)
    for elem in src.data:
        writer.write_int64(elem)


def cdr_body_to_py_Int64MultiArray(reader: CdrReader, dst: Int64MultiArray):
    cdr_body_to_py_MultiArrayLayout(reader, dst.layout)
    dst.data = [reader.read_int64() for _ in range(reader.read_uint32())]
    return dst


def py_to_cdr_Int64MultiArray(src: Int64MultiArray) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_Int64MultiArray(writer, src)
    return writer.bytes()


def cdr_to_py_Int64MultiArray(cdr_payload) -> Int64MultiArray:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = Int64MultiArray()
    return cdr_body_to_py_Int64MultiArray(reader, dst)
