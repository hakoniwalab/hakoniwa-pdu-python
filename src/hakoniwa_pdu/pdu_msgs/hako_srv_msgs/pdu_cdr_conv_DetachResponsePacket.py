from .pdu_pytype_DetachResponsePacket import DetachResponsePacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..hako_srv_msgs.pdu_cdr_conv_DetachResponse import *
from ..hako_srv_msgs.pdu_cdr_conv_ServiceResponseHeader import *



def py_to_cdr_body_DetachResponsePacket(writer: CdrWriter, src: DetachResponsePacket):
    py_to_cdr_body_ServiceResponseHeader(writer, src.header)
    py_to_cdr_body_DetachResponse(writer, src.body)


def cdr_body_to_py_DetachResponsePacket(reader: CdrReader, dst: DetachResponsePacket):
    cdr_body_to_py_ServiceResponseHeader(reader, dst.header)
    cdr_body_to_py_DetachResponse(reader, dst.body)
    return dst


def py_to_cdr_DetachResponsePacket(src: DetachResponsePacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_DetachResponsePacket(writer, src)
    return writer.bytes()


def cdr_to_py_DetachResponsePacket(cdr_payload) -> DetachResponsePacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = DetachResponsePacket()
    return cdr_body_to_py_DetachResponsePacket(reader, dst)
