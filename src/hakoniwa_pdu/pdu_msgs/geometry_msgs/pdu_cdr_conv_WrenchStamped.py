from .pdu_pytype_WrenchStamped import WrenchStamped
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_Header import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *
from ..geometry_msgs.pdu_cdr_conv_Vector3 import *
from ..geometry_msgs.pdu_cdr_conv_Wrench import *



def py_to_cdr_body_WrenchStamped(writer: CdrWriter, src: WrenchStamped):
    py_to_cdr_body_Header(writer, src.header)
    py_to_cdr_body_Wrench(writer, src.wrench)


def cdr_body_to_py_WrenchStamped(reader: CdrReader, dst: WrenchStamped):
    cdr_body_to_py_Header(reader, dst.header)
    cdr_body_to_py_Wrench(reader, dst.wrench)
    return dst


def py_to_cdr_WrenchStamped(src: WrenchStamped) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_WrenchStamped(writer, src)
    return writer.bytes()


def cdr_to_py_WrenchStamped(cdr_payload) -> WrenchStamped:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = WrenchStamped()
    return cdr_body_to_py_WrenchStamped(reader, dst)
