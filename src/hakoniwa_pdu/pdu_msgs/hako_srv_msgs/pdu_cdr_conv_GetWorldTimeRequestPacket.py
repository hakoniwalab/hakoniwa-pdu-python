from .pdu_pytype_GetWorldTimeRequestPacket import GetWorldTimeRequestPacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..hako_srv_msgs.pdu_cdr_conv_GetWorldTimeRequest import *
from ..hako_srv_msgs.pdu_cdr_conv_ServiceRequestHeader import *



def py_to_cdr_body_GetWorldTimeRequestPacket(writer: CdrWriter, src: GetWorldTimeRequestPacket):
    py_to_cdr_body_ServiceRequestHeader(writer, src.header)
    py_to_cdr_body_GetWorldTimeRequest(writer, src.body)


def cdr_body_to_py_GetWorldTimeRequestPacket(reader: CdrReader, dst: GetWorldTimeRequestPacket):
    cdr_body_to_py_ServiceRequestHeader(reader, dst.header)
    cdr_body_to_py_GetWorldTimeRequest(reader, dst.body)
    return dst


def py_to_cdr_GetWorldTimeRequestPacket(src: GetWorldTimeRequestPacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_GetWorldTimeRequestPacket(writer, src)
    return writer.bytes()


def cdr_to_py_GetWorldTimeRequestPacket(cdr_payload) -> GetWorldTimeRequestPacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = GetWorldTimeRequestPacket()
    return cdr_body_to_py_GetWorldTimeRequestPacket(reader, dst)
