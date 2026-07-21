from .pdu_pytype_MultiDOFJointTrajectory import MultiDOFJointTrajectory
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..builtin_interfaces.pdu_cdr_conv_Duration import *
from ..std_msgs.pdu_cdr_conv_Header import *
from ..trajectory_msgs.pdu_cdr_conv_MultiDOFJointTrajectoryPoint import *
from ..geometry_msgs.pdu_cdr_conv_Quaternion import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *
from ..geometry_msgs.pdu_cdr_conv_Transform import *
from ..geometry_msgs.pdu_cdr_conv_Twist import *
from ..geometry_msgs.pdu_cdr_conv_Vector3 import *



def py_to_cdr_body_MultiDOFJointTrajectory(writer: CdrWriter, src: MultiDOFJointTrajectory):
    py_to_cdr_body_Header(writer, src.header)
    writer.write_sequence_length(src.joint_names)
    for elem in src.joint_names:
        writer.write_string(elem)
    writer.write_sequence_length(src.points)
    for elem in src.points:
        py_to_cdr_body_MultiDOFJointTrajectoryPoint(writer, elem)


def cdr_body_to_py_MultiDOFJointTrajectory(reader: CdrReader, dst: MultiDOFJointTrajectory):
    cdr_body_to_py_Header(reader, dst.header)
    dst.joint_names = [reader.read_string() for _ in range(reader.read_uint32())]
    dst.points = []
    for _ in range(reader.read_uint32()):
        elem = MultiDOFJointTrajectoryPoint()
        cdr_body_to_py_MultiDOFJointTrajectoryPoint(reader, elem)
        dst.points.append(elem)
    return dst


def py_to_cdr_MultiDOFJointTrajectory(src: MultiDOFJointTrajectory) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_MultiDOFJointTrajectory(writer, src)
    return writer.bytes()


def cdr_to_py_MultiDOFJointTrajectory(cdr_payload) -> MultiDOFJointTrajectory:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = MultiDOFJointTrajectory()
    return cdr_body_to_py_MultiDOFJointTrajectory(reader, dst)
