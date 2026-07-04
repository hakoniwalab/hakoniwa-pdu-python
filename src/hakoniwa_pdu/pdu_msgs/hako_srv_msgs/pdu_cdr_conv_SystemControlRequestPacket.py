from .pdu_pytype_SystemControlRequestPacket import SystemControlRequestPacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..hako_srv_msgs.pdu_cdr_conv_ServiceRequestHeader import *
from ..hako_srv_msgs.pdu_cdr_conv_SystemControlRequest import *



def py_to_cdr_body_SystemControlRequestPacket(writer: CdrWriter, src: SystemControlRequestPacket):
    py_to_cdr_body_ServiceRequestHeader(writer, src.header)
    py_to_cdr_body_SystemControlRequest(writer, src.body)


def cdr_body_to_py_SystemControlRequestPacket(reader: CdrReader, dst: SystemControlRequestPacket):
    cdr_body_to_py_ServiceRequestHeader(reader, dst.header)
    cdr_body_to_py_SystemControlRequest(reader, dst.body)
    return dst


def py_to_cdr_SystemControlRequestPacket(src: SystemControlRequestPacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_SystemControlRequestPacket(writer, src)
    return writer.bytes()


def cdr_to_py_SystemControlRequestPacket(cdr_payload) -> SystemControlRequestPacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = SystemControlRequestPacket()
    return cdr_body_to_py_SystemControlRequestPacket(reader, dst)
