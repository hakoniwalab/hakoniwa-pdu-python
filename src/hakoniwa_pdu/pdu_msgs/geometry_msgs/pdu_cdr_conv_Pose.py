from .pdu_pytype_Pose import Pose
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..geometry_msgs.pdu_cdr_conv_Point import *
from ..geometry_msgs.pdu_cdr_conv_Quaternion import *



def py_to_cdr_body_Pose(writer: CdrWriter, src: Pose):
    py_to_cdr_body_Point(writer, src.position)
    py_to_cdr_body_Quaternion(writer, src.orientation)


def cdr_body_to_py_Pose(reader: CdrReader, dst: Pose):
    cdr_body_to_py_Point(reader, dst.position)
    cdr_body_to_py_Quaternion(reader, dst.orientation)
    return dst


def py_to_cdr_Pose(src: Pose) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_Pose(writer, src)
    return writer.bytes()


def cdr_to_py_Pose(cdr_payload) -> Pose:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = Pose()
    return cdr_body_to_py_Pose(reader, dst)
