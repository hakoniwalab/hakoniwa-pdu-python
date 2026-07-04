from .pdu_pytype_Pose2D import Pose2D
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_Pose2D(writer: CdrWriter, src: Pose2D):
    writer.write_float64(src.x)
    writer.write_float64(src.y)
    writer.write_float64(src.theta)


def cdr_body_to_py_Pose2D(reader: CdrReader, dst: Pose2D):
    dst.x = reader.read_float64()
    dst.y = reader.read_float64()
    dst.theta = reader.read_float64()
    return dst


def py_to_cdr_Pose2D(src: Pose2D) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_Pose2D(writer, src)
    return writer.bytes()


def cdr_to_py_Pose2D(cdr_payload) -> Pose2D:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = Pose2D()
    return cdr_body_to_py_Pose2D(reader, dst)
