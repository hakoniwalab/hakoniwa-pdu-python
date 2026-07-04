from .pdu_pytype_PoseArray import PoseArray
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_Header import *
from ..geometry_msgs.pdu_cdr_conv_Point import *
from ..geometry_msgs.pdu_cdr_conv_Pose import *
from ..geometry_msgs.pdu_cdr_conv_Quaternion import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *



def py_to_cdr_body_PoseArray(writer: CdrWriter, src: PoseArray):
    py_to_cdr_body_Header(writer, src.header)
    writer.write_sequence_length(src.poses)
    for elem in src.poses:
        py_to_cdr_body_Pose(writer, elem)


def cdr_body_to_py_PoseArray(reader: CdrReader, dst: PoseArray):
    cdr_body_to_py_Header(reader, dst.header)
    dst.poses = []
    for _ in range(reader.read_uint32()):
        elem = Pose()
        cdr_body_to_py_Pose(reader, elem)
        dst.poses.append(elem)
    return dst


def py_to_cdr_PoseArray(src: PoseArray) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_PoseArray(writer, src)
    return writer.bytes()


def cdr_to_py_PoseArray(cdr_payload) -> PoseArray:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = PoseArray()
    return cdr_body_to_py_PoseArray(reader, dst)
