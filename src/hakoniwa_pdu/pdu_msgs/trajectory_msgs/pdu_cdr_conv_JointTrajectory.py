from .pdu_pytype_JointTrajectory import JointTrajectory
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..builtin_interfaces.pdu_cdr_conv_Duration import *
from ..std_msgs.pdu_cdr_conv_Header import *
from ..trajectory_msgs.pdu_cdr_conv_JointTrajectoryPoint import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *



def py_to_cdr_body_JointTrajectory(writer: CdrWriter, src: JointTrajectory):
    py_to_cdr_body_Header(writer, src.header)
    writer.write_sequence_length(src.joint_names)
    for elem in src.joint_names:
        writer.write_string(elem)
    writer.write_sequence_length(src.points)
    for elem in src.points:
        py_to_cdr_body_JointTrajectoryPoint(writer, elem)


def cdr_body_to_py_JointTrajectory(reader: CdrReader, dst: JointTrajectory):
    cdr_body_to_py_Header(reader, dst.header)
    dst.joint_names = [reader.read_string() for _ in range(reader.read_uint32())]
    dst.points = []
    for _ in range(reader.read_uint32()):
        elem = JointTrajectoryPoint()
        cdr_body_to_py_JointTrajectoryPoint(reader, elem)
        dst.points.append(elem)
    return dst


def py_to_cdr_JointTrajectory(src: JointTrajectory) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_JointTrajectory(writer, src)
    return writer.bytes()


def cdr_to_py_JointTrajectory(cdr_payload) -> JointTrajectory:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = JointTrajectory()
    return cdr_body_to_py_JointTrajectory(reader, dst)
