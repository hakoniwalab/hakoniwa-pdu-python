from .pdu_pytype_TFMessage import TFMessage
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_Header import *
from ..geometry_msgs.pdu_cdr_conv_Quaternion import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *
from ..geometry_msgs.pdu_cdr_conv_Transform import *
from ..geometry_msgs.pdu_cdr_conv_TransformStamped import *
from ..geometry_msgs.pdu_cdr_conv_Vector3 import *



def py_to_cdr_body_TFMessage(writer: CdrWriter, src: TFMessage):
    writer.write_sequence_length(src.transforms)
    for elem in src.transforms:
        py_to_cdr_body_TransformStamped(writer, elem)


def cdr_body_to_py_TFMessage(reader: CdrReader, dst: TFMessage):
    dst.transforms = []
    for _ in range(reader.read_uint32()):
        elem = TransformStamped()
        cdr_body_to_py_TransformStamped(reader, elem)
        dst.transforms.append(elem)
    return dst


def py_to_cdr_TFMessage(src: TFMessage) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_TFMessage(writer, src)
    return writer.bytes()


def cdr_to_py_TFMessage(cdr_payload) -> TFMessage:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = TFMessage()
    return cdr_body_to_py_TFMessage(reader, dst)
