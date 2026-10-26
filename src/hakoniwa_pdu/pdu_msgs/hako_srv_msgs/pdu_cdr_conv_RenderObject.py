from .pdu_pytype_RenderObject import RenderObject
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..geometry_msgs.pdu_cdr_conv_Point import *
from ..geometry_msgs.pdu_cdr_conv_Pose import *
from ..geometry_msgs.pdu_cdr_conv_Quaternion import *



def py_to_cdr_body_RenderObject(writer: CdrWriter, src: RenderObject):
    writer.write_string(src.name)
    writer.write_string(src.model)
    py_to_cdr_body_Pose(writer, src.pose)


def cdr_body_to_py_RenderObject(reader: CdrReader, dst: RenderObject):
    dst.name = reader.read_string()
    dst.model = reader.read_string()
    cdr_body_to_py_Pose(reader, dst.pose)
    return dst


def py_to_cdr_RenderObject(src: RenderObject) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_RenderObject(writer, src)
    return writer.bytes()


def cdr_to_py_RenderObject(cdr_payload) -> RenderObject:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = RenderObject()
    return cdr_body_to_py_RenderObject(reader, dst)
