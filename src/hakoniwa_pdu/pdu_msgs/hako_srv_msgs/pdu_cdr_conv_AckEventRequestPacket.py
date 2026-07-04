from .pdu_pytype_AckEventRequestPacket import AckEventRequestPacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..hako_srv_msgs.pdu_cdr_conv_AckEventRequest import *
from ..hako_srv_msgs.pdu_cdr_conv_ServiceRequestHeader import *



def py_to_cdr_body_AckEventRequestPacket(writer: CdrWriter, src: AckEventRequestPacket):
    py_to_cdr_body_ServiceRequestHeader(writer, src.header)
    py_to_cdr_body_AckEventRequest(writer, src.body)


def cdr_body_to_py_AckEventRequestPacket(reader: CdrReader, dst: AckEventRequestPacket):
    cdr_body_to_py_ServiceRequestHeader(reader, dst.header)
    cdr_body_to_py_AckEventRequest(reader, dst.body)
    return dst


def py_to_cdr_AckEventRequestPacket(src: AckEventRequestPacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_AckEventRequestPacket(writer, src)
    return writer.bytes()


def cdr_to_py_AckEventRequestPacket(cdr_payload) -> AckEventRequestPacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = AckEventRequestPacket()
    return cdr_body_to_py_AckEventRequestPacket(reader, dst)
