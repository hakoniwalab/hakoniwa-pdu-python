from .pdu_pytype_SystemControlResponse import SystemControlResponse
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_SystemControlResponse(writer: CdrWriter, src: SystemControlResponse):
    writer.write_uint32(src.status_code)
    writer.write_string(src.message)


def cdr_body_to_py_SystemControlResponse(reader: CdrReader, dst: SystemControlResponse):
    dst.status_code = reader.read_uint32()
    dst.message = reader.read_string()
    return dst


def py_to_cdr_SystemControlResponse(src: SystemControlResponse) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_SystemControlResponse(writer, src)
    return writer.bytes()


def cdr_to_py_SystemControlResponse(cdr_payload) -> SystemControlResponse:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = SystemControlResponse()
    return cdr_body_to_py_SystemControlResponse(reader, dst)
