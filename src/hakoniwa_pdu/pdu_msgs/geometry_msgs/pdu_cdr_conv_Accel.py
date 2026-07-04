from .pdu_pytype_Accel import Accel
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..geometry_msgs.pdu_cdr_conv_Vector3 import *



def py_to_cdr_body_Accel(writer: CdrWriter, src: Accel):
    py_to_cdr_body_Vector3(writer, src.linear)
    py_to_cdr_body_Vector3(writer, src.angular)


def cdr_body_to_py_Accel(reader: CdrReader, dst: Accel):
    cdr_body_to_py_Vector3(reader, dst.linear)
    cdr_body_to_py_Vector3(reader, dst.angular)
    return dst


def py_to_cdr_Accel(src: Accel) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_Accel(writer, src)
    return writer.bytes()


def cdr_to_py_Accel(cdr_payload) -> Accel:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = Accel()
    return cdr_body_to_py_Accel(reader, dst)
