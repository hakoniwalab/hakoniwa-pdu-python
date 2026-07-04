from .pdu_pytype_GetSimStateRequest import GetSimStateRequest
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_GetSimStateRequest(writer: CdrWriter, src: GetSimStateRequest):
    writer.write_string(src.name)


def cdr_body_to_py_GetSimStateRequest(reader: CdrReader, dst: GetSimStateRequest):
    dst.name = reader.read_string()
    return dst


def py_to_cdr_GetSimStateRequest(src: GetSimStateRequest) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_GetSimStateRequest(writer, src)
    return writer.bytes()


def cdr_to_py_GetSimStateRequest(cdr_payload) -> GetSimStateRequest:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = GetSimStateRequest()
    return cdr_body_to_py_GetSimStateRequest(reader, dst)
