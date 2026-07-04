from .pdu_pytype_PointStamped import PointStamped
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_Header import *
from ..geometry_msgs.pdu_cdr_conv_Point import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *



def py_to_cdr_body_PointStamped(writer: CdrWriter, src: PointStamped):
    py_to_cdr_body_Header(writer, src.header)
    py_to_cdr_body_Point(writer, src.point)


def cdr_body_to_py_PointStamped(reader: CdrReader, dst: PointStamped):
    cdr_body_to_py_Header(reader, dst.header)
    cdr_body_to_py_Point(reader, dst.point)
    return dst


def py_to_cdr_PointStamped(src: PointStamped) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_PointStamped(writer, src)
    return writer.bytes()


def cdr_to_py_PointStamped(cdr_payload) -> PointStamped:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = PointStamped()
    return cdr_body_to_py_PointStamped(reader, dst)
