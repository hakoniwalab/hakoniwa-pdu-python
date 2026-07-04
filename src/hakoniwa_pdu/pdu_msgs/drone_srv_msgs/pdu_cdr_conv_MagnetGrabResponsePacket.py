from .pdu_pytype_MagnetGrabResponsePacket import MagnetGrabResponsePacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..drone_srv_msgs.pdu_cdr_conv_MagnetGrabResponse import *
from ..hako_srv_msgs.pdu_cdr_conv_ServiceResponseHeader import *



def py_to_cdr_body_MagnetGrabResponsePacket(writer: CdrWriter, src: MagnetGrabResponsePacket):
    py_to_cdr_body_ServiceResponseHeader(writer, src.header)
    py_to_cdr_body_MagnetGrabResponse(writer, src.body)


def cdr_body_to_py_MagnetGrabResponsePacket(reader: CdrReader, dst: MagnetGrabResponsePacket):
    cdr_body_to_py_ServiceResponseHeader(reader, dst.header)
    cdr_body_to_py_MagnetGrabResponse(reader, dst.body)
    return dst


def py_to_cdr_MagnetGrabResponsePacket(src: MagnetGrabResponsePacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_MagnetGrabResponsePacket(writer, src)
    return writer.bytes()


def cdr_to_py_MagnetGrabResponsePacket(cdr_payload) -> MagnetGrabResponsePacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = MagnetGrabResponsePacket()
    return cdr_body_to_py_MagnetGrabResponsePacket(reader, dst)
