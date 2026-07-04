from .pdu_pytype_Float64MultiArray import Float64MultiArray
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_MultiArrayDimension import *
from ..std_msgs.pdu_cdr_conv_MultiArrayLayout import *



def py_to_cdr_body_Float64MultiArray(writer: CdrWriter, src: Float64MultiArray):
    py_to_cdr_body_MultiArrayLayout(writer, src.layout)
    writer.write_sequence_length(src.data)
    for elem in src.data:
        writer.write_float64(elem)


def cdr_body_to_py_Float64MultiArray(reader: CdrReader, dst: Float64MultiArray):
    cdr_body_to_py_MultiArrayLayout(reader, dst.layout)
    dst.data = [reader.read_float64() for _ in range(reader.read_uint32())]
    return dst


def py_to_cdr_Float64MultiArray(src: Float64MultiArray) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_Float64MultiArray(writer, src)
    return writer.bytes()


def cdr_to_py_Float64MultiArray(cdr_payload) -> Float64MultiArray:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = Float64MultiArray()
    return cdr_body_to_py_Float64MultiArray(reader, dst)
