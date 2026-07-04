from .pdu_pytype_AckEventResponsePacket import AckEventResponsePacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..hako_srv_msgs.pdu_cdr_conv_AckEventResponse import *
from ..hako_srv_msgs.pdu_cdr_conv_ServiceResponseHeader import *



def py_to_cdr_body_AckEventResponsePacket(writer: CdrWriter, src: AckEventResponsePacket):
    py_to_cdr_body_ServiceResponseHeader(writer, src.header)
    py_to_cdr_body_AckEventResponse(writer, src.body)


def cdr_body_to_py_AckEventResponsePacket(reader: CdrReader, dst: AckEventResponsePacket):
    cdr_body_to_py_ServiceResponseHeader(reader, dst.header)
    cdr_body_to_py_AckEventResponse(reader, dst.body)
    return dst


def py_to_cdr_AckEventResponsePacket(src: AckEventResponsePacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_AckEventResponsePacket(writer, src)
    return writer.bytes()


def cdr_to_py_AckEventResponsePacket(cdr_payload) -> AckEventResponsePacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = AckEventResponsePacket()
    return cdr_body_to_py_AckEventResponsePacket(reader, dst)
