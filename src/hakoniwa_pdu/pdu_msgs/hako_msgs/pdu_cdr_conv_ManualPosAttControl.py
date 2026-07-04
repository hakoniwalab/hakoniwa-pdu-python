from .pdu_pytype_ManualPosAttControl import ManualPosAttControl
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..geometry_msgs.pdu_cdr_conv_Twist import *
from ..geometry_msgs.pdu_cdr_conv_Vector3 import *



def py_to_cdr_body_ManualPosAttControl(writer: CdrWriter, src: ManualPosAttControl):
    writer.write_bool(src.do_operation)
    py_to_cdr_body_Twist(writer, src.posatt)


def cdr_body_to_py_ManualPosAttControl(reader: CdrReader, dst: ManualPosAttControl):
    dst.do_operation = reader.read_bool()
    cdr_body_to_py_Twist(reader, dst.posatt)
    return dst


def py_to_cdr_ManualPosAttControl(src: ManualPosAttControl) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_ManualPosAttControl(writer, src)
    return writer.bytes()


def cdr_to_py_ManualPosAttControl(cdr_payload) -> ManualPosAttControl:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = ManualPosAttControl()
    return cdr_body_to_py_ManualPosAttControl(reader, dst)
