from .pdu_pytype_QuaternionStamped import QuaternionStamped
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_Header import *
from ..geometry_msgs.pdu_cdr_conv_Quaternion import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *



def py_to_cdr_body_QuaternionStamped(writer: CdrWriter, src: QuaternionStamped):
    py_to_cdr_body_Header(writer, src.header)
    py_to_cdr_body_Quaternion(writer, src.quaternion)


def cdr_body_to_py_QuaternionStamped(reader: CdrReader, dst: QuaternionStamped):
    cdr_body_to_py_Header(reader, dst.header)
    cdr_body_to_py_Quaternion(reader, dst.quaternion)
    return dst


def py_to_cdr_QuaternionStamped(src: QuaternionStamped) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_QuaternionStamped(writer, src)
    return writer.bytes()


def cdr_to_py_QuaternionStamped(cdr_payload) -> QuaternionStamped:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = QuaternionStamped()
    return cdr_body_to_py_QuaternionStamped(reader, dst)
