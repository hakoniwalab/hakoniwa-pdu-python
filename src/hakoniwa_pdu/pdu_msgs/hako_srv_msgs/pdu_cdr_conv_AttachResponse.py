from .pdu_pytype_AttachResponse import AttachResponse
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..hako_srv_msgs.pdu_cdr_conv_LogicalTime import *



def py_to_cdr_body_AttachResponse(writer: CdrWriter, src: AttachResponse):
    writer.write_uint32(src.result_code)
    writer.write_uint64(src.session_id)
    py_to_cdr_body_LogicalTime(writer, src.world_time)
    writer.write_uint64(src.delta_asset_tick)


def cdr_body_to_py_AttachResponse(reader: CdrReader, dst: AttachResponse):
    dst.result_code = reader.read_uint32()
    dst.session_id = reader.read_uint64()
    cdr_body_to_py_LogicalTime(reader, dst.world_time)
    dst.delta_asset_tick = reader.read_uint64()
    return dst


def py_to_cdr_AttachResponse(src: AttachResponse) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_AttachResponse(writer, src)
    return writer.bytes()


def cdr_to_py_AttachResponse(cdr_payload) -> AttachResponse:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = AttachResponse()
    return cdr_body_to_py_AttachResponse(reader, dst)
