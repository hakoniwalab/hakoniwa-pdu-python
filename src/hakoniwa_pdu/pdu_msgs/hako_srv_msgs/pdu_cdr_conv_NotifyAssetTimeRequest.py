from .pdu_pytype_NotifyAssetTimeRequest import NotifyAssetTimeRequest
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..hako_srv_msgs.pdu_cdr_conv_LogicalTime import *



def py_to_cdr_body_NotifyAssetTimeRequest(writer: CdrWriter, src: NotifyAssetTimeRequest):
    writer.write_uint64(src.session_id)
    py_to_cdr_body_LogicalTime(writer, src.asset_time)


def cdr_body_to_py_NotifyAssetTimeRequest(reader: CdrReader, dst: NotifyAssetTimeRequest):
    dst.session_id = reader.read_uint64()
    cdr_body_to_py_LogicalTime(reader, dst.asset_time)
    return dst


def py_to_cdr_NotifyAssetTimeRequest(src: NotifyAssetTimeRequest) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_NotifyAssetTimeRequest(writer, src)
    return writer.bytes()


def cdr_to_py_NotifyAssetTimeRequest(cdr_payload) -> NotifyAssetTimeRequest:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = NotifyAssetTimeRequest()
    return cdr_body_to_py_NotifyAssetTimeRequest(reader, dst)
