from .pdu_pytype_SimControlRequestPacket import SimControlRequestPacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..hako_srv_msgs.pdu_cdr_conv_ServiceRequestHeader import *
from ..hako_srv_msgs.pdu_cdr_conv_SimControlRequest import *



def py_to_cdr_body_SimControlRequestPacket(writer: CdrWriter, src: SimControlRequestPacket):
    py_to_cdr_body_ServiceRequestHeader(writer, src.header)
    py_to_cdr_body_SimControlRequest(writer, src.body)


def cdr_body_to_py_SimControlRequestPacket(reader: CdrReader, dst: SimControlRequestPacket):
    cdr_body_to_py_ServiceRequestHeader(reader, dst.header)
    cdr_body_to_py_SimControlRequest(reader, dst.body)
    return dst


def py_to_cdr_SimControlRequestPacket(src: SimControlRequestPacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_SimControlRequestPacket(writer, src)
    return writer.bytes()


def cdr_to_py_SimControlRequestPacket(cdr_payload) -> SimControlRequestPacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = SimControlRequestPacket()
    return cdr_body_to_py_SimControlRequestPacket(reader, dst)
