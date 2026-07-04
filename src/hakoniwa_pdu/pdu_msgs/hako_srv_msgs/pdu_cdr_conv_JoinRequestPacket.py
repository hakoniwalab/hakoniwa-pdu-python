from .pdu_pytype_JoinRequestPacket import JoinRequestPacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..hako_srv_msgs.pdu_cdr_conv_JoinRequest import *
from ..hako_srv_msgs.pdu_cdr_conv_ServiceRequestHeader import *



def py_to_cdr_body_JoinRequestPacket(writer: CdrWriter, src: JoinRequestPacket):
    py_to_cdr_body_ServiceRequestHeader(writer, src.header)
    py_to_cdr_body_JoinRequest(writer, src.body)


def cdr_body_to_py_JoinRequestPacket(reader: CdrReader, dst: JoinRequestPacket):
    cdr_body_to_py_ServiceRequestHeader(reader, dst.header)
    cdr_body_to_py_JoinRequest(reader, dst.body)
    return dst


def py_to_cdr_JoinRequestPacket(src: JoinRequestPacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_JoinRequestPacket(writer, src)
    return writer.bytes()


def cdr_to_py_JoinRequestPacket(cdr_payload) -> JoinRequestPacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = JoinRequestPacket()
    return cdr_body_to_py_JoinRequestPacket(reader, dst)
