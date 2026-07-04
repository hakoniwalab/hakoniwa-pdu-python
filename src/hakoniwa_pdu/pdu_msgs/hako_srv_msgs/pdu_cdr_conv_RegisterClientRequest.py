from .pdu_pytype_RegisterClientRequest import RegisterClientRequest
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_RegisterClientRequest(writer: CdrWriter, src: RegisterClientRequest):
    writer.write_uint32(src.dummy)


def cdr_body_to_py_RegisterClientRequest(reader: CdrReader, dst: RegisterClientRequest):
    dst.dummy = reader.read_uint32()
    return dst


def py_to_cdr_RegisterClientRequest(src: RegisterClientRequest) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_RegisterClientRequest(writer, src)
    return writer.bytes()


def cdr_to_py_RegisterClientRequest(cdr_payload) -> RegisterClientRequest:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = RegisterClientRequest()
    return cdr_body_to_py_RegisterClientRequest(reader, dst)
