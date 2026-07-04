from .pdu_pytype_SimControlResponse import SimControlResponse
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_SimControlResponse(writer: CdrWriter, src: SimControlResponse):
    writer.write_uint32(src.status_code)
    writer.write_string(src.message)


def cdr_body_to_py_SimControlResponse(reader: CdrReader, dst: SimControlResponse):
    dst.status_code = reader.read_uint32()
    dst.message = reader.read_string()
    return dst


def py_to_cdr_SimControlResponse(src: SimControlResponse) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_SimControlResponse(writer, src)
    return writer.bytes()


def cdr_to_py_SimControlResponse(cdr_payload) -> SimControlResponse:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = SimControlResponse()
    return cdr_body_to_py_SimControlResponse(reader, dst)
