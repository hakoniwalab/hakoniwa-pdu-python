from .pdu_pytype_AttachRequestPacket import AttachRequestPacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..hako_srv_msgs.pdu_cdr_conv_AttachRequest import *
from ..hako_srv_msgs.pdu_cdr_conv_ServiceRequestHeader import *



def py_to_cdr_body_AttachRequestPacket(writer: CdrWriter, src: AttachRequestPacket):
    py_to_cdr_body_ServiceRequestHeader(writer, src.header)
    py_to_cdr_body_AttachRequest(writer, src.body)


def cdr_body_to_py_AttachRequestPacket(reader: CdrReader, dst: AttachRequestPacket):
    cdr_body_to_py_ServiceRequestHeader(reader, dst.header)
    cdr_body_to_py_AttachRequest(reader, dst.body)
    return dst


def py_to_cdr_AttachRequestPacket(src: AttachRequestPacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_AttachRequestPacket(writer, src)
    return writer.bytes()


def cdr_to_py_AttachRequestPacket(cdr_payload) -> AttachRequestPacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = AttachRequestPacket()
    return cdr_body_to_py_AttachRequestPacket(reader, dst)
