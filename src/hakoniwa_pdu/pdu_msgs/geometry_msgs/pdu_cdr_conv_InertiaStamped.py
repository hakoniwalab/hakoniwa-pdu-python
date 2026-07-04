from .pdu_pytype_InertiaStamped import InertiaStamped
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_Header import *
from ..geometry_msgs.pdu_cdr_conv_Inertia import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *
from ..geometry_msgs.pdu_cdr_conv_Vector3 import *



def py_to_cdr_body_InertiaStamped(writer: CdrWriter, src: InertiaStamped):
    py_to_cdr_body_Header(writer, src.header)
    py_to_cdr_body_Inertia(writer, src.inertia)


def cdr_body_to_py_InertiaStamped(reader: CdrReader, dst: InertiaStamped):
    cdr_body_to_py_Header(reader, dst.header)
    cdr_body_to_py_Inertia(reader, dst.inertia)
    return dst


def py_to_cdr_InertiaStamped(src: InertiaStamped) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_InertiaStamped(writer, src)
    return writer.bytes()


def cdr_to_py_InertiaStamped(cdr_payload) -> InertiaStamped:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = InertiaStamped()
    return cdr_body_to_py_InertiaStamped(reader, dst)
