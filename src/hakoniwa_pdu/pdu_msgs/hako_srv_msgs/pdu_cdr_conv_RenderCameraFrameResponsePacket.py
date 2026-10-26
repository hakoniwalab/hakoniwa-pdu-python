from .pdu_pytype_RenderCameraFrameResponsePacket import RenderCameraFrameResponsePacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_Header import *
from ..sensor_msgs.pdu_cdr_conv_Image import *
from ..hako_srv_msgs.pdu_cdr_conv_RenderCameraFrameResponse import *
from ..hako_srv_msgs.pdu_cdr_conv_ServiceResponseHeader import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *



def py_to_cdr_body_RenderCameraFrameResponsePacket(writer: CdrWriter, src: RenderCameraFrameResponsePacket):
    py_to_cdr_body_ServiceResponseHeader(writer, src.header)
    py_to_cdr_body_RenderCameraFrameResponse(writer, src.body)


def cdr_body_to_py_RenderCameraFrameResponsePacket(reader: CdrReader, dst: RenderCameraFrameResponsePacket):
    cdr_body_to_py_ServiceResponseHeader(reader, dst.header)
    cdr_body_to_py_RenderCameraFrameResponse(reader, dst.body)
    return dst


def py_to_cdr_RenderCameraFrameResponsePacket(src: RenderCameraFrameResponsePacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_RenderCameraFrameResponsePacket(writer, src)
    return writer.bytes()


def cdr_to_py_RenderCameraFrameResponsePacket(cdr_payload) -> RenderCameraFrameResponsePacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = RenderCameraFrameResponsePacket()
    return cdr_body_to_py_RenderCameraFrameResponsePacket(reader, dst)
