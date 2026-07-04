from .pdu_pytype_GetEventResponse import GetEventResponse
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_GetEventResponse(writer: CdrWriter, src: GetEventResponse):
    writer.write_uint32(src.event_code)


def cdr_body_to_py_GetEventResponse(reader: CdrReader, dst: GetEventResponse):
    dst.event_code = reader.read_uint32()
    return dst


def py_to_cdr_GetEventResponse(src: GetEventResponse) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_GetEventResponse(writer, src)
    return writer.bytes()


def cdr_to_py_GetEventResponse(cdr_payload) -> GetEventResponse:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = GetEventResponse()
    return cdr_body_to_py_GetEventResponse(reader, dst)
