from .pdu_pytype_CameraSetTiltResponsePacket import CameraSetTiltResponsePacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..drone_srv_msgs.pdu_cdr_conv_CameraSetTiltResponse import *
from ..hako_srv_msgs.pdu_cdr_conv_ServiceResponseHeader import *



def py_to_cdr_body_CameraSetTiltResponsePacket(writer: CdrWriter, src: CameraSetTiltResponsePacket):
    py_to_cdr_body_ServiceResponseHeader(writer, src.header)
    py_to_cdr_body_CameraSetTiltResponse(writer, src.body)


def cdr_body_to_py_CameraSetTiltResponsePacket(reader: CdrReader, dst: CameraSetTiltResponsePacket):
    cdr_body_to_py_ServiceResponseHeader(reader, dst.header)
    cdr_body_to_py_CameraSetTiltResponse(reader, dst.body)
    return dst


def py_to_cdr_CameraSetTiltResponsePacket(src: CameraSetTiltResponsePacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_CameraSetTiltResponsePacket(writer, src)
    return writer.bytes()


def cdr_to_py_CameraSetTiltResponsePacket(cdr_payload) -> CameraSetTiltResponsePacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = CameraSetTiltResponsePacket()
    return cdr_body_to_py_CameraSetTiltResponsePacket(reader, dst)
