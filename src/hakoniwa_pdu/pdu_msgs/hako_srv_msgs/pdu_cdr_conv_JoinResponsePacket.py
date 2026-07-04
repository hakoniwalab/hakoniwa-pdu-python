from .pdu_pytype_JoinResponsePacket import JoinResponsePacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..hako_srv_msgs.pdu_cdr_conv_JoinResponse import *
from ..hako_srv_msgs.pdu_cdr_conv_ServiceResponseHeader import *



def py_to_cdr_body_JoinResponsePacket(writer: CdrWriter, src: JoinResponsePacket):
    py_to_cdr_body_ServiceResponseHeader(writer, src.header)
    py_to_cdr_body_JoinResponse(writer, src.body)


def cdr_body_to_py_JoinResponsePacket(reader: CdrReader, dst: JoinResponsePacket):
    cdr_body_to_py_ServiceResponseHeader(reader, dst.header)
    cdr_body_to_py_JoinResponse(reader, dst.body)
    return dst


def py_to_cdr_JoinResponsePacket(src: JoinResponsePacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_JoinResponsePacket(writer, src)
    return writer.bytes()


def cdr_to_py_JoinResponsePacket(cdr_payload) -> JoinResponsePacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = JoinResponsePacket()
    return cdr_body_to_py_JoinResponsePacket(reader, dst)
