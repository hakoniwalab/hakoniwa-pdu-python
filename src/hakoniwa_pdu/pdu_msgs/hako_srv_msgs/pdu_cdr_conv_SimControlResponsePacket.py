from .pdu_pytype_SimControlResponsePacket import SimControlResponsePacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..hako_srv_msgs.pdu_cdr_conv_ServiceResponseHeader import *
from ..hako_srv_msgs.pdu_cdr_conv_SimControlResponse import *



def py_to_cdr_body_SimControlResponsePacket(writer: CdrWriter, src: SimControlResponsePacket):
    py_to_cdr_body_ServiceResponseHeader(writer, src.header)
    py_to_cdr_body_SimControlResponse(writer, src.body)


def cdr_body_to_py_SimControlResponsePacket(reader: CdrReader, dst: SimControlResponsePacket):
    cdr_body_to_py_ServiceResponseHeader(reader, dst.header)
    cdr_body_to_py_SimControlResponse(reader, dst.body)
    return dst


def py_to_cdr_SimControlResponsePacket(src: SimControlResponsePacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_SimControlResponsePacket(writer, src)
    return writer.bytes()


def cdr_to_py_SimControlResponsePacket(cdr_payload) -> SimControlResponsePacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = SimControlResponsePacket()
    return cdr_body_to_py_SimControlResponsePacket(reader, dst)
