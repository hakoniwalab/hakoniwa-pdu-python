from .pdu_pytype_NotifyAssetTimeRequestPacket import NotifyAssetTimeRequestPacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..hako_srv_msgs.pdu_cdr_conv_LogicalTime import *
from ..hako_srv_msgs.pdu_cdr_conv_NotifyAssetTimeRequest import *
from ..hako_srv_msgs.pdu_cdr_conv_ServiceRequestHeader import *



def py_to_cdr_body_NotifyAssetTimeRequestPacket(writer: CdrWriter, src: NotifyAssetTimeRequestPacket):
    py_to_cdr_body_ServiceRequestHeader(writer, src.header)
    py_to_cdr_body_NotifyAssetTimeRequest(writer, src.body)


def cdr_body_to_py_NotifyAssetTimeRequestPacket(reader: CdrReader, dst: NotifyAssetTimeRequestPacket):
    cdr_body_to_py_ServiceRequestHeader(reader, dst.header)
    cdr_body_to_py_NotifyAssetTimeRequest(reader, dst.body)
    return dst


def py_to_cdr_NotifyAssetTimeRequestPacket(src: NotifyAssetTimeRequestPacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_NotifyAssetTimeRequestPacket(writer, src)
    return writer.bytes()


def cdr_to_py_NotifyAssetTimeRequestPacket(cdr_payload) -> NotifyAssetTimeRequestPacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = NotifyAssetTimeRequestPacket()
    return cdr_body_to_py_NotifyAssetTimeRequestPacket(reader, dst)
