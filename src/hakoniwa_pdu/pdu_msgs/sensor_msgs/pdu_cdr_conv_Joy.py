from .pdu_pytype_Joy import Joy
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_Header import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *



def py_to_cdr_body_Joy(writer: CdrWriter, src: Joy):
    py_to_cdr_body_Header(writer, src.header)
    writer.write_sequence_length(src.axes)
    for elem in src.axes:
        writer.write_float32(elem)
    writer.write_sequence_length(src.buttons)
    for elem in src.buttons:
        writer.write_int32(elem)


def cdr_body_to_py_Joy(reader: CdrReader, dst: Joy):
    cdr_body_to_py_Header(reader, dst.header)
    dst.axes = [reader.read_float32() for _ in range(reader.read_uint32())]
    dst.buttons = [reader.read_int32() for _ in range(reader.read_uint32())]
    return dst


def py_to_cdr_Joy(src: Joy) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_Joy(writer, src)
    return writer.bytes()


def cdr_to_py_Joy(cdr_payload) -> Joy:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = Joy()
    return cdr_body_to_py_Joy(reader, dst)
