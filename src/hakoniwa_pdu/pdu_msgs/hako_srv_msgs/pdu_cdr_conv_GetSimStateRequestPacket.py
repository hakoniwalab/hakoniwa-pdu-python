from .pdu_pytype_GetSimStateRequestPacket import GetSimStateRequestPacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..hako_srv_msgs.pdu_cdr_conv_GetSimStateRequest import *
from ..hako_srv_msgs.pdu_cdr_conv_ServiceRequestHeader import *



def py_to_cdr_body_GetSimStateRequestPacket(writer: CdrWriter, src: GetSimStateRequestPacket):
    py_to_cdr_body_ServiceRequestHeader(writer, src.header)
    py_to_cdr_body_GetSimStateRequest(writer, src.body)


def cdr_body_to_py_GetSimStateRequestPacket(reader: CdrReader, dst: GetSimStateRequestPacket):
    cdr_body_to_py_ServiceRequestHeader(reader, dst.header)
    cdr_body_to_py_GetSimStateRequest(reader, dst.body)
    return dst


def py_to_cdr_GetSimStateRequestPacket(src: GetSimStateRequestPacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_GetSimStateRequestPacket(writer, src)
    return writer.bytes()


def cdr_to_py_GetSimStateRequestPacket(cdr_payload) -> GetSimStateRequestPacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = GetSimStateRequestPacket()
    return cdr_body_to_py_GetSimStateRequestPacket(reader, dst)
