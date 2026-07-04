from .pdu_pytype_CameraCaptureImageResponsePacket import CameraCaptureImageResponsePacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..drone_srv_msgs.pdu_cdr_conv_CameraCaptureImageResponse import *
from ..hako_srv_msgs.pdu_cdr_conv_ServiceResponseHeader import *



def py_to_cdr_body_CameraCaptureImageResponsePacket(writer: CdrWriter, src: CameraCaptureImageResponsePacket):
    py_to_cdr_body_ServiceResponseHeader(writer, src.header)
    py_to_cdr_body_CameraCaptureImageResponse(writer, src.body)


def cdr_body_to_py_CameraCaptureImageResponsePacket(reader: CdrReader, dst: CameraCaptureImageResponsePacket):
    cdr_body_to_py_ServiceResponseHeader(reader, dst.header)
    cdr_body_to_py_CameraCaptureImageResponse(reader, dst.body)
    return dst


def py_to_cdr_CameraCaptureImageResponsePacket(src: CameraCaptureImageResponsePacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_CameraCaptureImageResponsePacket(writer, src)
    return writer.bytes()


def cdr_to_py_CameraCaptureImageResponsePacket(cdr_payload) -> CameraCaptureImageResponsePacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = CameraCaptureImageResponsePacket()
    return cdr_body_to_py_CameraCaptureImageResponsePacket(reader, dst)
