from .pdu_pytype_Int16MultiArray import Int16MultiArray
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_MultiArrayDimension import *
from ..std_msgs.pdu_cdr_conv_MultiArrayLayout import *



def py_to_cdr_body_Int16MultiArray(writer: CdrWriter, src: Int16MultiArray):
    py_to_cdr_body_MultiArrayLayout(writer, src.layout)
    writer.write_sequence_length(src.data)
    for elem in src.data:
        writer.write_int16(elem)


def cdr_body_to_py_Int16MultiArray(reader: CdrReader, dst: Int16MultiArray):
    cdr_body_to_py_MultiArrayLayout(reader, dst.layout)
    dst.data = [reader.read_int16() for _ in range(reader.read_uint32())]
    return dst


def py_to_cdr_Int16MultiArray(src: Int16MultiArray) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_Int16MultiArray(writer, src)
    return writer.bytes()


def cdr_to_py_Int16MultiArray(cdr_payload) -> Int16MultiArray:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = Int16MultiArray()
    return cdr_body_to_py_Int16MultiArray(reader, dst)
