from .pdu_pytype_Vector3Stamped import Vector3Stamped
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_Header import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *
from ..geometry_msgs.pdu_cdr_conv_Vector3 import *



def py_to_cdr_body_Vector3Stamped(writer: CdrWriter, src: Vector3Stamped):
    py_to_cdr_body_Header(writer, src.header)
    py_to_cdr_body_Vector3(writer, src.vector)


def cdr_body_to_py_Vector3Stamped(reader: CdrReader, dst: Vector3Stamped):
    cdr_body_to_py_Header(reader, dst.header)
    cdr_body_to_py_Vector3(reader, dst.vector)
    return dst


def py_to_cdr_Vector3Stamped(src: Vector3Stamped) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_Vector3Stamped(writer, src)
    return writer.bytes()


def cdr_to_py_Vector3Stamped(cdr_payload) -> Vector3Stamped:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = Vector3Stamped()
    return cdr_body_to_py_Vector3Stamped(reader, dst)
