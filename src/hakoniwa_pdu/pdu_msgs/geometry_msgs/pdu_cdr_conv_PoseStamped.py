from .pdu_pytype_PoseStamped import PoseStamped
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_Header import *
from ..geometry_msgs.pdu_cdr_conv_Point import *
from ..geometry_msgs.pdu_cdr_conv_Pose import *
from ..geometry_msgs.pdu_cdr_conv_Quaternion import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *



def py_to_cdr_body_PoseStamped(writer: CdrWriter, src: PoseStamped):
    py_to_cdr_body_Header(writer, src.header)
    py_to_cdr_body_Pose(writer, src.pose)


def cdr_body_to_py_PoseStamped(reader: CdrReader, dst: PoseStamped):
    cdr_body_to_py_Header(reader, dst.header)
    cdr_body_to_py_Pose(reader, dst.pose)
    return dst


def py_to_cdr_PoseStamped(src: PoseStamped) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_PoseStamped(writer, src)
    return writer.bytes()


def cdr_to_py_PoseStamped(cdr_payload) -> PoseStamped:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = PoseStamped()
    return cdr_body_to_py_PoseStamped(reader, dst)
