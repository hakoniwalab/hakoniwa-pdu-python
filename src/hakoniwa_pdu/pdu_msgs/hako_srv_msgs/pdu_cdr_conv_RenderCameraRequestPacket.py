from .pdu_pytype_RenderCameraRequestPacket import RenderCameraRequestPacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..geometry_msgs.pdu_cdr_conv_Point import *
from ..geometry_msgs.pdu_cdr_conv_Pose import *
from ..geometry_msgs.pdu_cdr_conv_Quaternion import *
from ..hako_srv_msgs.pdu_cdr_conv_RenderCameraRequest import *
from ..hako_srv_msgs.pdu_cdr_conv_ServiceRequestHeader import *



def py_to_cdr_body_RenderCameraRequestPacket(writer: CdrWriter, src: RenderCameraRequestPacket):
    py_to_cdr_body_ServiceRequestHeader(writer, src.header)
    py_to_cdr_body_RenderCameraRequest(writer, src.body)


def cdr_body_to_py_RenderCameraRequestPacket(reader: CdrReader, dst: RenderCameraRequestPacket):
    cdr_body_to_py_ServiceRequestHeader(reader, dst.header)
    cdr_body_to_py_RenderCameraRequest(reader, dst.body)
    return dst


def py_to_cdr_RenderCameraRequestPacket(src: RenderCameraRequestPacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_RenderCameraRequestPacket(writer, src)
    return writer.bytes()


def cdr_to_py_RenderCameraRequestPacket(cdr_payload) -> RenderCameraRequestPacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = RenderCameraRequestPacket()
    return cdr_body_to_py_RenderCameraRequestPacket(reader, dst)
