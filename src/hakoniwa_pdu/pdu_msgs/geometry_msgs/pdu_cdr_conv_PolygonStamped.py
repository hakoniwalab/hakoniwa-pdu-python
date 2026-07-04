from .pdu_pytype_PolygonStamped import PolygonStamped
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_Header import *
from ..geometry_msgs.pdu_cdr_conv_Point32 import *
from ..geometry_msgs.pdu_cdr_conv_Polygon import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *



def py_to_cdr_body_PolygonStamped(writer: CdrWriter, src: PolygonStamped):
    py_to_cdr_body_Header(writer, src.header)
    py_to_cdr_body_Polygon(writer, src.polygon)


def cdr_body_to_py_PolygonStamped(reader: CdrReader, dst: PolygonStamped):
    cdr_body_to_py_Header(reader, dst.header)
    cdr_body_to_py_Polygon(reader, dst.polygon)
    return dst


def py_to_cdr_PolygonStamped(src: PolygonStamped) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_PolygonStamped(writer, src)
    return writer.bytes()


def cdr_to_py_PolygonStamped(cdr_payload) -> PolygonStamped:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = PolygonStamped()
    return cdr_body_to_py_PolygonStamped(reader, dst)
