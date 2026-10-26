from .pdu_pytype_RenderCameraFrameRequestPacket import RenderCameraFrameRequestPacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..geometry_msgs.pdu_cdr_conv_Point import *
from ..geometry_msgs.pdu_cdr_conv_Pose import *
from ..geometry_msgs.pdu_cdr_conv_Quaternion import *
from ..hako_srv_msgs.pdu_cdr_conv_RenderCameraFrameRequest import *
from ..hako_srv_msgs.pdu_cdr_conv_RenderObject import *
from ..hako_srv_msgs.pdu_cdr_conv_ServiceRequestHeader import *



def py_to_cdr_body_RenderCameraFrameRequestPacket(writer: CdrWriter, src: RenderCameraFrameRequestPacket):
    py_to_cdr_body_ServiceRequestHeader(writer, src.header)
    py_to_cdr_body_RenderCameraFrameRequest(writer, src.body)


def cdr_body_to_py_RenderCameraFrameRequestPacket(reader: CdrReader, dst: RenderCameraFrameRequestPacket):
    cdr_body_to_py_ServiceRequestHeader(reader, dst.header)
    cdr_body_to_py_RenderCameraFrameRequest(reader, dst.body)
    return dst


def py_to_cdr_RenderCameraFrameRequestPacket(src: RenderCameraFrameRequestPacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_RenderCameraFrameRequestPacket(writer, src)
    return writer.bytes()


def cdr_to_py_RenderCameraFrameRequestPacket(cdr_payload) -> RenderCameraFrameRequestPacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = RenderCameraFrameRequestPacket()
    return cdr_body_to_py_RenderCameraFrameRequestPacket(reader, dst)
