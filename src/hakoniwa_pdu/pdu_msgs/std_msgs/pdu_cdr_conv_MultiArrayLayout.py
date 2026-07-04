from .pdu_pytype_MultiArrayLayout import MultiArrayLayout
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_MultiArrayDimension import *



def py_to_cdr_body_MultiArrayLayout(writer: CdrWriter, src: MultiArrayLayout):
    writer.write_sequence_length(src.dim)
    for elem in src.dim:
        py_to_cdr_body_MultiArrayDimension(writer, elem)
    writer.write_uint32(src.data_offset)


def cdr_body_to_py_MultiArrayLayout(reader: CdrReader, dst: MultiArrayLayout):
    dst.dim = []
    for _ in range(reader.read_uint32()):
        elem = MultiArrayDimension()
        cdr_body_to_py_MultiArrayDimension(reader, elem)
        dst.dim.append(elem)
    dst.data_offset = reader.read_uint32()
    return dst


def py_to_cdr_MultiArrayLayout(src: MultiArrayLayout) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_MultiArrayLayout(writer, src)
    return writer.bytes()


def cdr_to_py_MultiArrayLayout(cdr_payload) -> MultiArrayLayout:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = MultiArrayLayout()
    return cdr_body_to_py_MultiArrayLayout(reader, dst)
