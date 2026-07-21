from .pdu_pytype_GetWorldTimeResponse import GetWorldTimeResponse
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..hako_srv_msgs.pdu_cdr_conv_LogicalTime import *



def py_to_cdr_body_GetWorldTimeResponse(writer: CdrWriter, src: GetWorldTimeResponse):
    writer.write_uint32(src.result_code)
    py_to_cdr_body_LogicalTime(writer, src.world_time)


def cdr_body_to_py_GetWorldTimeResponse(reader: CdrReader, dst: GetWorldTimeResponse):
    dst.result_code = reader.read_uint32()
    cdr_body_to_py_LogicalTime(reader, dst.world_time)
    return dst


def py_to_cdr_GetWorldTimeResponse(src: GetWorldTimeResponse) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_GetWorldTimeResponse(writer, src)
    return writer.bytes()


def cdr_to_py_GetWorldTimeResponse(cdr_payload) -> GetWorldTimeResponse:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = GetWorldTimeResponse()
    return cdr_body_to_py_GetWorldTimeResponse(reader, dst)
