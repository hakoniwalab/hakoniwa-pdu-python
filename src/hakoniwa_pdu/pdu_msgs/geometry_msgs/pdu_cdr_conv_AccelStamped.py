from .pdu_pytype_AccelStamped import AccelStamped
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..geometry_msgs.pdu_cdr_conv_Accel import *
from ..std_msgs.pdu_cdr_conv_Header import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *
from ..geometry_msgs.pdu_cdr_conv_Vector3 import *



def py_to_cdr_body_AccelStamped(writer: CdrWriter, src: AccelStamped):
    py_to_cdr_body_Header(writer, src.header)
    py_to_cdr_body_Accel(writer, src.accel)


def cdr_body_to_py_AccelStamped(reader: CdrReader, dst: AccelStamped):
    cdr_body_to_py_Header(reader, dst.header)
    cdr_body_to_py_Accel(reader, dst.accel)
    return dst


def py_to_cdr_AccelStamped(src: AccelStamped) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_AccelStamped(writer, src)
    return writer.bytes()


def cdr_to_py_AccelStamped(cdr_payload) -> AccelStamped:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = AccelStamped()
    return cdr_body_to_py_AccelStamped(reader, dst)
