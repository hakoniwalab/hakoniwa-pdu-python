from .pdu_pytype_Path import Path
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_Header import *
from ..geometry_msgs.pdu_cdr_conv_Point import *
from ..geometry_msgs.pdu_cdr_conv_Pose import *
from ..geometry_msgs.pdu_cdr_conv_PoseStamped import *
from ..geometry_msgs.pdu_cdr_conv_Quaternion import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *



def py_to_cdr_body_Path(writer: CdrWriter, src: Path):
    py_to_cdr_body_Header(writer, src.header)
    writer.write_sequence_length(src.poses)
    for elem in src.poses:
        py_to_cdr_body_PoseStamped(writer, elem)


def cdr_body_to_py_Path(reader: CdrReader, dst: Path):
    cdr_body_to_py_Header(reader, dst.header)
    dst.poses = []
    for _ in range(reader.read_uint32()):
        elem = PoseStamped()
        cdr_body_to_py_PoseStamped(reader, elem)
        dst.poses.append(elem)
    return dst


def py_to_cdr_Path(src: Path) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_Path(writer, src)
    return writer.bytes()


def cdr_to_py_Path(cdr_payload) -> Path:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = Path()
    return cdr_body_to_py_Path(reader, dst)
