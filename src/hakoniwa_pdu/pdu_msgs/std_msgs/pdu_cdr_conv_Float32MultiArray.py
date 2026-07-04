from .pdu_pytype_Float32MultiArray import Float32MultiArray
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_MultiArrayDimension import *
from ..std_msgs.pdu_cdr_conv_MultiArrayLayout import *



def py_to_cdr_body_Float32MultiArray(writer: CdrWriter, src: Float32MultiArray):
    py_to_cdr_body_MultiArrayLayout(writer, src.layout)
    writer.write_sequence_length(src.data)
    for elem in src.data:
        writer.write_float32(elem)


def cdr_body_to_py_Float32MultiArray(reader: CdrReader, dst: Float32MultiArray):
    cdr_body_to_py_MultiArrayLayout(reader, dst.layout)
    dst.data = [reader.read_float32() for _ in range(reader.read_uint32())]
    return dst


def py_to_cdr_Float32MultiArray(src: Float32MultiArray) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_Float32MultiArray(writer, src)
    return writer.bytes()


def cdr_to_py_Float32MultiArray(cdr_payload) -> Float32MultiArray:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = Float32MultiArray()
    return cdr_body_to_py_Float32MultiArray(reader, dst)
