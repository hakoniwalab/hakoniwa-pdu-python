from .pdu_pytype_DetachRequestPacket import DetachRequestPacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..hako_srv_msgs.pdu_cdr_conv_DetachRequest import *
from ..hako_srv_msgs.pdu_cdr_conv_ServiceRequestHeader import *



def py_to_cdr_body_DetachRequestPacket(writer: CdrWriter, src: DetachRequestPacket):
    py_to_cdr_body_ServiceRequestHeader(writer, src.header)
    py_to_cdr_body_DetachRequest(writer, src.body)


def cdr_body_to_py_DetachRequestPacket(reader: CdrReader, dst: DetachRequestPacket):
    cdr_body_to_py_ServiceRequestHeader(reader, dst.header)
    cdr_body_to_py_DetachRequest(reader, dst.body)
    return dst


def py_to_cdr_DetachRequestPacket(src: DetachRequestPacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_DetachRequestPacket(writer, src)
    return writer.bytes()


def cdr_to_py_DetachRequestPacket(cdr_payload) -> DetachRequestPacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = DetachRequestPacket()
    return cdr_body_to_py_DetachRequestPacket(reader, dst)
