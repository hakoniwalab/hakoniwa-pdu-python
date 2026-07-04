from .pdu_pytype_GetEventResponsePacket import GetEventResponsePacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..hako_srv_msgs.pdu_cdr_conv_GetEventResponse import *
from ..hako_srv_msgs.pdu_cdr_conv_ServiceResponseHeader import *



def py_to_cdr_body_GetEventResponsePacket(writer: CdrWriter, src: GetEventResponsePacket):
    py_to_cdr_body_ServiceResponseHeader(writer, src.header)
    py_to_cdr_body_GetEventResponse(writer, src.body)


def cdr_body_to_py_GetEventResponsePacket(reader: CdrReader, dst: GetEventResponsePacket):
    cdr_body_to_py_ServiceResponseHeader(reader, dst.header)
    cdr_body_to_py_GetEventResponse(reader, dst.body)
    return dst


def py_to_cdr_GetEventResponsePacket(src: GetEventResponsePacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_GetEventResponsePacket(writer, src)
    return writer.bytes()


def cdr_to_py_GetEventResponsePacket(cdr_payload) -> GetEventResponsePacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = GetEventResponsePacket()
    return cdr_body_to_py_GetEventResponsePacket(reader, dst)
