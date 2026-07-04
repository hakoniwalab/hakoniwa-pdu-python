from .pdu_pytype_GetSimStateResponsePacket import GetSimStateResponsePacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..hako_srv_msgs.pdu_cdr_conv_GetSimStateResponse import *
from ..hako_srv_msgs.pdu_cdr_conv_ServiceResponseHeader import *



def py_to_cdr_body_GetSimStateResponsePacket(writer: CdrWriter, src: GetSimStateResponsePacket):
    py_to_cdr_body_ServiceResponseHeader(writer, src.header)
    py_to_cdr_body_GetSimStateResponse(writer, src.body)


def cdr_body_to_py_GetSimStateResponsePacket(reader: CdrReader, dst: GetSimStateResponsePacket):
    cdr_body_to_py_ServiceResponseHeader(reader, dst.header)
    cdr_body_to_py_GetSimStateResponse(reader, dst.body)
    return dst


def py_to_cdr_GetSimStateResponsePacket(src: GetSimStateResponsePacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_GetSimStateResponsePacket(writer, src)
    return writer.bytes()


def cdr_to_py_GetSimStateResponsePacket(cdr_payload) -> GetSimStateResponsePacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = GetSimStateResponsePacket()
    return cdr_body_to_py_GetSimStateResponsePacket(reader, dst)
