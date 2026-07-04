from .pdu_pytype_CameraCaptureImageRequestPacket import CameraCaptureImageRequestPacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..drone_srv_msgs.pdu_cdr_conv_CameraCaptureImageRequest import *
from ..hako_srv_msgs.pdu_cdr_conv_ServiceRequestHeader import *



def py_to_cdr_body_CameraCaptureImageRequestPacket(writer: CdrWriter, src: CameraCaptureImageRequestPacket):
    py_to_cdr_body_ServiceRequestHeader(writer, src.header)
    py_to_cdr_body_CameraCaptureImageRequest(writer, src.body)


def cdr_body_to_py_CameraCaptureImageRequestPacket(reader: CdrReader, dst: CameraCaptureImageRequestPacket):
    cdr_body_to_py_ServiceRequestHeader(reader, dst.header)
    cdr_body_to_py_CameraCaptureImageRequest(reader, dst.body)
    return dst


def py_to_cdr_CameraCaptureImageRequestPacket(src: CameraCaptureImageRequestPacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_CameraCaptureImageRequestPacket(writer, src)
    return writer.bytes()


def cdr_to_py_CameraCaptureImageRequestPacket(cdr_payload) -> CameraCaptureImageRequestPacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = CameraCaptureImageRequestPacket()
    return cdr_body_to_py_CameraCaptureImageRequestPacket(reader, dst)
