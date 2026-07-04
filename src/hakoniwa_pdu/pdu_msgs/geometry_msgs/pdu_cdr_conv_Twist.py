from .pdu_pytype_Twist import Twist
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..geometry_msgs.pdu_cdr_conv_Vector3 import *



def py_to_cdr_body_Twist(writer: CdrWriter, src: Twist):
    py_to_cdr_body_Vector3(writer, src.linear)
    py_to_cdr_body_Vector3(writer, src.angular)


def cdr_body_to_py_Twist(reader: CdrReader, dst: Twist):
    cdr_body_to_py_Vector3(reader, dst.linear)
    cdr_body_to_py_Vector3(reader, dst.angular)
    return dst


def py_to_cdr_Twist(src: Twist) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_Twist(writer, src)
    return writer.bytes()


def cdr_to_py_Twist(cdr_payload) -> Twist:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = Twist()
    return cdr_body_to_py_Twist(reader, dst)
