from .pdu_pytype_GetWorldTimeRequest import GetWorldTimeRequest
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_GetWorldTimeRequest(writer: CdrWriter, src: GetWorldTimeRequest):
    writer.write_uint64(src.session_id)


def cdr_body_to_py_GetWorldTimeRequest(reader: CdrReader, dst: GetWorldTimeRequest):
    dst.session_id = reader.read_uint64()
    return dst


def py_to_cdr_GetWorldTimeRequest(src: GetWorldTimeRequest) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_GetWorldTimeRequest(writer, src)
    return writer.bytes()


def cdr_to_py_GetWorldTimeRequest(cdr_payload) -> GetWorldTimeRequest:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = GetWorldTimeRequest()
    return cdr_body_to_py_GetWorldTimeRequest(reader, dst)
