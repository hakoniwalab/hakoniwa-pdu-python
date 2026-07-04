from .pdu_pytype_GetEventRequestPacket import GetEventRequestPacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..hako_srv_msgs.pdu_cdr_conv_GetEventRequest import *
from ..hako_srv_msgs.pdu_cdr_conv_ServiceRequestHeader import *



def py_to_cdr_body_GetEventRequestPacket(writer: CdrWriter, src: GetEventRequestPacket):
    py_to_cdr_body_ServiceRequestHeader(writer, src.header)
    py_to_cdr_body_GetEventRequest(writer, src.body)


def cdr_body_to_py_GetEventRequestPacket(reader: CdrReader, dst: GetEventRequestPacket):
    cdr_body_to_py_ServiceRequestHeader(reader, dst.header)
    cdr_body_to_py_GetEventRequest(reader, dst.body)
    return dst


def py_to_cdr_GetEventRequestPacket(src: GetEventRequestPacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_GetEventRequestPacket(writer, src)
    return writer.bytes()


def cdr_to_py_GetEventRequestPacket(cdr_payload) -> GetEventRequestPacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = GetEventRequestPacket()
    return cdr_body_to_py_GetEventRequestPacket(reader, dst)
