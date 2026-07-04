from .pdu_pytype_GetEventRequest import GetEventRequest
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_GetEventRequest(writer: CdrWriter, src: GetEventRequest):
    writer.write_string(src.name)


def cdr_body_to_py_GetEventRequest(reader: CdrReader, dst: GetEventRequest):
    dst.name = reader.read_string()
    return dst


def py_to_cdr_GetEventRequest(src: GetEventRequest) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_GetEventRequest(writer, src)
    return writer.bytes()


def cdr_to_py_GetEventRequest(cdr_payload) -> GetEventRequest:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = GetEventRequest()
    return cdr_body_to_py_GetEventRequest(reader, dst)
