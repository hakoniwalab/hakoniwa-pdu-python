from .pdu_pytype_RegisterClientRequestPacket import RegisterClientRequestPacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..hako_srv_msgs.pdu_cdr_conv_RegisterClientRequest import *
from ..hako_srv_msgs.pdu_cdr_conv_ServiceRequestHeader import *



def py_to_cdr_body_RegisterClientRequestPacket(writer: CdrWriter, src: RegisterClientRequestPacket):
    py_to_cdr_body_ServiceRequestHeader(writer, src.header)
    py_to_cdr_body_RegisterClientRequest(writer, src.body)


def cdr_body_to_py_RegisterClientRequestPacket(reader: CdrReader, dst: RegisterClientRequestPacket):
    cdr_body_to_py_ServiceRequestHeader(reader, dst.header)
    cdr_body_to_py_RegisterClientRequest(reader, dst.body)
    return dst


def py_to_cdr_RegisterClientRequestPacket(src: RegisterClientRequestPacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_RegisterClientRequestPacket(writer, src)
    return writer.bytes()


def cdr_to_py_RegisterClientRequestPacket(cdr_payload) -> RegisterClientRequestPacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = RegisterClientRequestPacket()
    return cdr_body_to_py_RegisterClientRequestPacket(reader, dst)
