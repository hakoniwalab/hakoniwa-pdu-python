from .pdu_pytype_SystemControlResponsePacket import SystemControlResponsePacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..hako_srv_msgs.pdu_cdr_conv_ServiceResponseHeader import *
from ..hako_srv_msgs.pdu_cdr_conv_SystemControlResponse import *



def py_to_cdr_body_SystemControlResponsePacket(writer: CdrWriter, src: SystemControlResponsePacket):
    py_to_cdr_body_ServiceResponseHeader(writer, src.header)
    py_to_cdr_body_SystemControlResponse(writer, src.body)


def cdr_body_to_py_SystemControlResponsePacket(reader: CdrReader, dst: SystemControlResponsePacket):
    cdr_body_to_py_ServiceResponseHeader(reader, dst.header)
    cdr_body_to_py_SystemControlResponse(reader, dst.body)
    return dst


def py_to_cdr_SystemControlResponsePacket(src: SystemControlResponsePacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_SystemControlResponsePacket(writer, src)
    return writer.bytes()


def cdr_to_py_SystemControlResponsePacket(cdr_payload) -> SystemControlResponsePacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = SystemControlResponsePacket()
    return cdr_body_to_py_SystemControlResponsePacket(reader, dst)
