from .pdu_pytype_MagnetGrabRequestPacket import MagnetGrabRequestPacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..drone_srv_msgs.pdu_cdr_conv_MagnetGrabRequest import *
from ..hako_srv_msgs.pdu_cdr_conv_ServiceRequestHeader import *



def py_to_cdr_body_MagnetGrabRequestPacket(writer: CdrWriter, src: MagnetGrabRequestPacket):
    py_to_cdr_body_ServiceRequestHeader(writer, src.header)
    py_to_cdr_body_MagnetGrabRequest(writer, src.body)


def cdr_body_to_py_MagnetGrabRequestPacket(reader: CdrReader, dst: MagnetGrabRequestPacket):
    cdr_body_to_py_ServiceRequestHeader(reader, dst.header)
    cdr_body_to_py_MagnetGrabRequest(reader, dst.body)
    return dst


def py_to_cdr_MagnetGrabRequestPacket(src: MagnetGrabRequestPacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_MagnetGrabRequestPacket(writer, src)
    return writer.bytes()


def cdr_to_py_MagnetGrabRequestPacket(cdr_payload) -> MagnetGrabRequestPacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = MagnetGrabRequestPacket()
    return cdr_body_to_py_MagnetGrabRequestPacket(reader, dst)
