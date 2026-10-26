from .pdu_pytype_RenderCameraResponsePacket import RenderCameraResponsePacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_Header import *
from ..sensor_msgs.pdu_cdr_conv_Image import *
from ..hako_srv_msgs.pdu_cdr_conv_RenderCameraResponse import *
from ..hako_srv_msgs.pdu_cdr_conv_ServiceResponseHeader import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *



def py_to_cdr_body_RenderCameraResponsePacket(writer: CdrWriter, src: RenderCameraResponsePacket):
    py_to_cdr_body_ServiceResponseHeader(writer, src.header)
    py_to_cdr_body_RenderCameraResponse(writer, src.body)


def cdr_body_to_py_RenderCameraResponsePacket(reader: CdrReader, dst: RenderCameraResponsePacket):
    cdr_body_to_py_ServiceResponseHeader(reader, dst.header)
    cdr_body_to_py_RenderCameraResponse(reader, dst.body)
    return dst


def py_to_cdr_RenderCameraResponsePacket(src: RenderCameraResponsePacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_RenderCameraResponsePacket(writer, src)
    return writer.bytes()


def cdr_to_py_RenderCameraResponsePacket(cdr_payload) -> RenderCameraResponsePacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = RenderCameraResponsePacket()
    return cdr_body_to_py_RenderCameraResponsePacket(reader, dst)
