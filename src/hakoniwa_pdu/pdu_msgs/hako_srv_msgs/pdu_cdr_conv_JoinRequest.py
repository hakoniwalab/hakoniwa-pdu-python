from .pdu_pytype_JoinRequest import JoinRequest
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_JoinRequest(writer: CdrWriter, src: JoinRequest):
    writer.write_string(src.name)


def cdr_body_to_py_JoinRequest(reader: CdrReader, dst: JoinRequest):
    dst.name = reader.read_string()
    return dst


def py_to_cdr_JoinRequest(src: JoinRequest) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_JoinRequest(writer, src)
    return writer.bytes()


def cdr_to_py_JoinRequest(cdr_payload) -> JoinRequest:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = JoinRequest()
    return cdr_body_to_py_JoinRequest(reader, dst)
