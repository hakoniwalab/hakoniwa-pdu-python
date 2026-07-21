from .pdu_pytype_JointTrajectoryPoint import JointTrajectoryPoint
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..builtin_interfaces.pdu_cdr_conv_Duration import *



def py_to_cdr_body_JointTrajectoryPoint(writer: CdrWriter, src: JointTrajectoryPoint):
    writer.write_sequence_length(src.positions)
    for elem in src.positions:
        writer.write_float64(elem)
    writer.write_sequence_length(src.velocities)
    for elem in src.velocities:
        writer.write_float64(elem)
    writer.write_sequence_length(src.accelerations)
    for elem in src.accelerations:
        writer.write_float64(elem)
    writer.write_sequence_length(src.effort)
    for elem in src.effort:
        writer.write_float64(elem)
    py_to_cdr_body_Duration(writer, src.time_from_start)


def cdr_body_to_py_JointTrajectoryPoint(reader: CdrReader, dst: JointTrajectoryPoint):
    dst.positions = [reader.read_float64() for _ in range(reader.read_uint32())]
    dst.velocities = [reader.read_float64() for _ in range(reader.read_uint32())]
    dst.accelerations = [reader.read_float64() for _ in range(reader.read_uint32())]
    dst.effort = [reader.read_float64() for _ in range(reader.read_uint32())]
    cdr_body_to_py_Duration(reader, dst.time_from_start)
    return dst


def py_to_cdr_JointTrajectoryPoint(src: JointTrajectoryPoint) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_JointTrajectoryPoint(writer, src)
    return writer.bytes()


def cdr_to_py_JointTrajectoryPoint(cdr_payload) -> JointTrajectoryPoint:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = JointTrajectoryPoint()
    return cdr_body_to_py_JointTrajectoryPoint(reader, dst)
