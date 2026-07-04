from .pdu_pytype_TwistStamped import TwistStamped
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_Header import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *
from ..geometry_msgs.pdu_cdr_conv_Twist import *
from ..geometry_msgs.pdu_cdr_conv_Vector3 import *



def py_to_cdr_body_TwistStamped(writer: CdrWriter, src: TwistStamped):
    py_to_cdr_body_Header(writer, src.header)
    py_to_cdr_body_Twist(writer, src.twist)


def cdr_body_to_py_TwistStamped(reader: CdrReader, dst: TwistStamped):
    cdr_body_to_py_Header(reader, dst.header)
    cdr_body_to_py_Twist(reader, dst.twist)
    return dst


def py_to_cdr_TwistStamped(src: TwistStamped) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_TwistStamped(writer, src)
    return writer.bytes()


def cdr_to_py_TwistStamped(cdr_payload) -> TwistStamped:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = TwistStamped()
    return cdr_body_to_py_TwistStamped(reader, dst)
