from .pdu_pytype_Polygon import Polygon
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..geometry_msgs.pdu_cdr_conv_Point32 import *



def py_to_cdr_body_Polygon(writer: CdrWriter, src: Polygon):
    writer.write_sequence_length(src.points)
    for elem in src.points:
        py_to_cdr_body_Point32(writer, elem)


def cdr_body_to_py_Polygon(reader: CdrReader, dst: Polygon):
    dst.points = []
    for _ in range(reader.read_uint32()):
        elem = Point32()
        cdr_body_to_py_Point32(reader, elem)
        dst.points.append(elem)
    return dst


def py_to_cdr_Polygon(src: Polygon) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_Polygon(writer, src)
    return writer.bytes()


def cdr_to_py_Polygon(cdr_payload) -> Polygon:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = Polygon()
    return cdr_body_to_py_Polygon(reader, dst)
