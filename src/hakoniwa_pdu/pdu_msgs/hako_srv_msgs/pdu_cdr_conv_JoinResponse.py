from .pdu_pytype_JoinResponse import JoinResponse
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_JoinResponse(writer: CdrWriter, src: JoinResponse):
    writer.write_uint32(src.status_code)
    writer.write_string(src.message)


def cdr_body_to_py_JoinResponse(reader: CdrReader, dst: JoinResponse):
    dst.status_code = reader.read_uint32()
    dst.message = reader.read_string()
    return dst


def py_to_cdr_JoinResponse(src: JoinResponse) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_JoinResponse(writer, src)
    return writer.bytes()


def cdr_to_py_JoinResponse(cdr_payload) -> JoinResponse:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = JoinResponse()
    return cdr_body_to_py_JoinResponse(reader, dst)
