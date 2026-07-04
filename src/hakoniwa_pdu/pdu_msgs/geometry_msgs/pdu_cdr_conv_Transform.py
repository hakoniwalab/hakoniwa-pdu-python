from .pdu_pytype_Transform import Transform
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..geometry_msgs.pdu_cdr_conv_Quaternion import *
from ..geometry_msgs.pdu_cdr_conv_Vector3 import *



def py_to_cdr_body_Transform(writer: CdrWriter, src: Transform):
    py_to_cdr_body_Vector3(writer, src.translation)
    py_to_cdr_body_Quaternion(writer, src.rotation)


def cdr_body_to_py_Transform(reader: CdrReader, dst: Transform):
    cdr_body_to_py_Vector3(reader, dst.translation)
    cdr_body_to_py_Quaternion(reader, dst.rotation)
    return dst


def py_to_cdr_Transform(src: Transform) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_Transform(writer, src)
    return writer.bytes()


def cdr_to_py_Transform(cdr_payload) -> Transform:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = Transform()
    return cdr_body_to_py_Transform(reader, dst)
