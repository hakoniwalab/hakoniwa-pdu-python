from .pdu_pytype_AttachResponsePacket import AttachResponsePacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..hako_srv_msgs.pdu_cdr_conv_AttachResponse import *
from ..hako_srv_msgs.pdu_cdr_conv_LogicalTime import *
from ..hako_srv_msgs.pdu_cdr_conv_ServiceResponseHeader import *



def py_to_cdr_body_AttachResponsePacket(writer: CdrWriter, src: AttachResponsePacket):
    py_to_cdr_body_ServiceResponseHeader(writer, src.header)
    py_to_cdr_body_AttachResponse(writer, src.body)


def cdr_body_to_py_AttachResponsePacket(reader: CdrReader, dst: AttachResponsePacket):
    cdr_body_to_py_ServiceResponseHeader(reader, dst.header)
    cdr_body_to_py_AttachResponse(reader, dst.body)
    return dst


def py_to_cdr_AttachResponsePacket(src: AttachResponsePacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_AttachResponsePacket(writer, src)
    return writer.bytes()


def cdr_to_py_AttachResponsePacket(cdr_payload) -> AttachResponsePacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = AttachResponsePacket()
    return cdr_body_to_py_AttachResponsePacket(reader, dst)
