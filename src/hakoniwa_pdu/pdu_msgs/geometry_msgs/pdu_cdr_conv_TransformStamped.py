from .pdu_pytype_TransformStamped import TransformStamped
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_Header import *
from ..geometry_msgs.pdu_cdr_conv_Quaternion import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *
from ..geometry_msgs.pdu_cdr_conv_Transform import *
from ..geometry_msgs.pdu_cdr_conv_Vector3 import *



def py_to_cdr_body_TransformStamped(writer: CdrWriter, src: TransformStamped):
    py_to_cdr_body_Header(writer, src.header)
    writer.write_string(src.child_frame_id)
    py_to_cdr_body_Transform(writer, src.transform)


def cdr_body_to_py_TransformStamped(reader: CdrReader, dst: TransformStamped):
    cdr_body_to_py_Header(reader, dst.header)
    dst.child_frame_id = reader.read_string()
    cdr_body_to_py_Transform(reader, dst.transform)
    return dst


def py_to_cdr_TransformStamped(src: TransformStamped) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_TransformStamped(writer, src)
    return writer.bytes()


def cdr_to_py_TransformStamped(cdr_payload) -> TransformStamped:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = TransformStamped()
    return cdr_body_to_py_TransformStamped(reader, dst)
