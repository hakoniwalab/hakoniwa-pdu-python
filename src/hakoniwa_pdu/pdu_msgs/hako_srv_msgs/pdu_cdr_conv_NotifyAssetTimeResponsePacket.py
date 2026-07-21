from .pdu_pytype_NotifyAssetTimeResponsePacket import NotifyAssetTimeResponsePacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..hako_srv_msgs.pdu_cdr_conv_NotifyAssetTimeResponse import *
from ..hako_srv_msgs.pdu_cdr_conv_ServiceResponseHeader import *



def py_to_cdr_body_NotifyAssetTimeResponsePacket(writer: CdrWriter, src: NotifyAssetTimeResponsePacket):
    py_to_cdr_body_ServiceResponseHeader(writer, src.header)
    py_to_cdr_body_NotifyAssetTimeResponse(writer, src.body)


def cdr_body_to_py_NotifyAssetTimeResponsePacket(reader: CdrReader, dst: NotifyAssetTimeResponsePacket):
    cdr_body_to_py_ServiceResponseHeader(reader, dst.header)
    cdr_body_to_py_NotifyAssetTimeResponse(reader, dst.body)
    return dst


def py_to_cdr_NotifyAssetTimeResponsePacket(src: NotifyAssetTimeResponsePacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_NotifyAssetTimeResponsePacket(writer, src)
    return writer.bytes()


def cdr_to_py_NotifyAssetTimeResponsePacket(cdr_payload) -> NotifyAssetTimeResponsePacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = NotifyAssetTimeResponsePacket()
    return cdr_body_to_py_NotifyAssetTimeResponsePacket(reader, dst)
