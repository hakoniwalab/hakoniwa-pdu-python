from .pdu_pytype_CameraSetTiltRequestPacket import CameraSetTiltRequestPacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..drone_srv_msgs.pdu_cdr_conv_CameraSetTiltRequest import *
from ..hako_srv_msgs.pdu_cdr_conv_ServiceRequestHeader import *



def py_to_cdr_body_CameraSetTiltRequestPacket(writer: CdrWriter, src: CameraSetTiltRequestPacket):
    py_to_cdr_body_ServiceRequestHeader(writer, src.header)
    py_to_cdr_body_CameraSetTiltRequest(writer, src.body)


def cdr_body_to_py_CameraSetTiltRequestPacket(reader: CdrReader, dst: CameraSetTiltRequestPacket):
    cdr_body_to_py_ServiceRequestHeader(reader, dst.header)
    cdr_body_to_py_CameraSetTiltRequest(reader, dst.body)
    return dst


def py_to_cdr_CameraSetTiltRequestPacket(src: CameraSetTiltRequestPacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_CameraSetTiltRequestPacket(writer, src)
    return writer.bytes()


def cdr_to_py_CameraSetTiltRequestPacket(cdr_payload) -> CameraSetTiltRequestPacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = CameraSetTiltRequestPacket()
    return cdr_body_to_py_CameraSetTiltRequestPacket(reader, dst)
