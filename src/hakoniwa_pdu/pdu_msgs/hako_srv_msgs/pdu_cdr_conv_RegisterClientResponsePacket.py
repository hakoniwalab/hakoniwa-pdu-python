from .pdu_pytype_RegisterClientResponsePacket import RegisterClientResponsePacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..hako_srv_msgs.pdu_cdr_conv_RegisterClientResponse import *
from ..hako_srv_msgs.pdu_cdr_conv_ServiceResponseHeader import *



def py_to_cdr_body_RegisterClientResponsePacket(writer: CdrWriter, src: RegisterClientResponsePacket):
    py_to_cdr_body_ServiceResponseHeader(writer, src.header)
    py_to_cdr_body_RegisterClientResponse(writer, src.body)


def cdr_body_to_py_RegisterClientResponsePacket(reader: CdrReader, dst: RegisterClientResponsePacket):
    cdr_body_to_py_ServiceResponseHeader(reader, dst.header)
    cdr_body_to_py_RegisterClientResponse(reader, dst.body)
    return dst


def py_to_cdr_RegisterClientResponsePacket(src: RegisterClientResponsePacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_RegisterClientResponsePacket(writer, src)
    return writer.bytes()


def cdr_to_py_RegisterClientResponsePacket(cdr_payload) -> RegisterClientResponsePacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = RegisterClientResponsePacket()
    return cdr_body_to_py_RegisterClientResponsePacket(reader, dst)
