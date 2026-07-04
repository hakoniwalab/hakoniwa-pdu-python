from .pdu_pytype_Wrench import Wrench
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..geometry_msgs.pdu_cdr_conv_Vector3 import *



def py_to_cdr_body_Wrench(writer: CdrWriter, src: Wrench):
    py_to_cdr_body_Vector3(writer, src.force)
    py_to_cdr_body_Vector3(writer, src.torque)


def cdr_body_to_py_Wrench(reader: CdrReader, dst: Wrench):
    cdr_body_to_py_Vector3(reader, dst.force)
    cdr_body_to_py_Vector3(reader, dst.torque)
    return dst


def py_to_cdr_Wrench(src: Wrench) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_Wrench(writer, src)
    return writer.bytes()


def cdr_to_py_Wrench(cdr_payload) -> Wrench:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = Wrench()
    return cdr_body_to_py_Wrench(reader, dst)
