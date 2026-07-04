from .pdu_pytype_PoseWithCovariance import PoseWithCovariance
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..geometry_msgs.pdu_cdr_conv_Point import *
from ..geometry_msgs.pdu_cdr_conv_Pose import *
from ..geometry_msgs.pdu_cdr_conv_Quaternion import *



def py_to_cdr_body_PoseWithCovariance(writer: CdrWriter, src: PoseWithCovariance):
    py_to_cdr_body_Pose(writer, src.pose)
    values = src.covariance
    for i in range(36):
        writer.write_float64(values[i] if i < len(values) else 0.0)


def cdr_body_to_py_PoseWithCovariance(reader: CdrReader, dst: PoseWithCovariance):
    cdr_body_to_py_Pose(reader, dst.pose)
    dst.covariance = [reader.read_float64() for _ in range(36)]
    return dst


def py_to_cdr_PoseWithCovariance(src: PoseWithCovariance) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_PoseWithCovariance(writer, src)
    return writer.bytes()


def cdr_to_py_PoseWithCovariance(cdr_payload) -> PoseWithCovariance:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = PoseWithCovariance()
    return cdr_body_to_py_PoseWithCovariance(reader, dst)
