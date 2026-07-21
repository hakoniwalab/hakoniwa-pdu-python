from .pdu_pytype_MultiDOFJointTrajectoryPoint import MultiDOFJointTrajectoryPoint
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..builtin_interfaces.pdu_cdr_conv_Duration import *
from ..geometry_msgs.pdu_cdr_conv_Quaternion import *
from ..geometry_msgs.pdu_cdr_conv_Transform import *
from ..geometry_msgs.pdu_cdr_conv_Twist import *
from ..geometry_msgs.pdu_cdr_conv_Vector3 import *



def py_to_cdr_body_MultiDOFJointTrajectoryPoint(writer: CdrWriter, src: MultiDOFJointTrajectoryPoint):
    writer.write_sequence_length(src.transforms)
    for elem in src.transforms:
        py_to_cdr_body_Transform(writer, elem)
    writer.write_sequence_length(src.velocities)
    for elem in src.velocities:
        py_to_cdr_body_Twist(writer, elem)
    writer.write_sequence_length(src.accelerations)
    for elem in src.accelerations:
        py_to_cdr_body_Twist(writer, elem)
    py_to_cdr_body_Duration(writer, src.time_from_start)


def cdr_body_to_py_MultiDOFJointTrajectoryPoint(reader: CdrReader, dst: MultiDOFJointTrajectoryPoint):
    dst.transforms = []
    for _ in range(reader.read_uint32()):
        elem = Transform()
        cdr_body_to_py_Transform(reader, elem)
        dst.transforms.append(elem)
    dst.velocities = []
    for _ in range(reader.read_uint32()):
        elem = Twist()
        cdr_body_to_py_Twist(reader, elem)
        dst.velocities.append(elem)
    dst.accelerations = []
    for _ in range(reader.read_uint32()):
        elem = Twist()
        cdr_body_to_py_Twist(reader, elem)
        dst.accelerations.append(elem)
    cdr_body_to_py_Duration(reader, dst.time_from_start)
    return dst


def py_to_cdr_MultiDOFJointTrajectoryPoint(src: MultiDOFJointTrajectoryPoint) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_MultiDOFJointTrajectoryPoint(writer, src)
    return writer.bytes()


def cdr_to_py_MultiDOFJointTrajectoryPoint(cdr_payload) -> MultiDOFJointTrajectoryPoint:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = MultiDOFJointTrajectoryPoint()
    return cdr_body_to_py_MultiDOFJointTrajectoryPoint(reader, dst)
