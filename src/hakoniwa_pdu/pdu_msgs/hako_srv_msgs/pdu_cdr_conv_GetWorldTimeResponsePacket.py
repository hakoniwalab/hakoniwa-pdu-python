from .pdu_pytype_GetWorldTimeResponsePacket import GetWorldTimeResponsePacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..hako_srv_msgs.pdu_cdr_conv_GetWorldTimeResponse import *
from ..hako_srv_msgs.pdu_cdr_conv_LogicalTime import *
from ..hako_srv_msgs.pdu_cdr_conv_ServiceResponseHeader import *



def py_to_cdr_body_GetWorldTimeResponsePacket(writer: CdrWriter, src: GetWorldTimeResponsePacket):
    py_to_cdr_body_ServiceResponseHeader(writer, src.header)
    py_to_cdr_body_GetWorldTimeResponse(writer, src.body)


def cdr_body_to_py_GetWorldTimeResponsePacket(reader: CdrReader, dst: GetWorldTimeResponsePacket):
    cdr_body_to_py_ServiceResponseHeader(reader, dst.header)
    cdr_body_to_py_GetWorldTimeResponse(reader, dst.body)
    return dst


def py_to_cdr_GetWorldTimeResponsePacket(src: GetWorldTimeResponsePacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_GetWorldTimeResponsePacket(writer, src)
    return writer.bytes()


def cdr_to_py_GetWorldTimeResponsePacket(cdr_payload) -> GetWorldTimeResponsePacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = GetWorldTimeResponsePacket()
    return cdr_body_to_py_GetWorldTimeResponsePacket(reader, dst)
