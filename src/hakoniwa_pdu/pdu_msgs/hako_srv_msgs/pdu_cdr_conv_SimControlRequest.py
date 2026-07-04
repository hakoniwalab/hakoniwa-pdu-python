from .pdu_pytype_SimControlRequest import SimControlRequest
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_SimControlRequest(writer: CdrWriter, src: SimControlRequest):
    writer.write_string(src.name)
    writer.write_uint32(src.op)


def cdr_body_to_py_SimControlRequest(reader: CdrReader, dst: SimControlRequest):
    dst.name = reader.read_string()
    dst.op = reader.read_uint32()
    return dst


def py_to_cdr_SimControlRequest(src: SimControlRequest) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_SimControlRequest(writer, src)
    return writer.bytes()


def cdr_to_py_SimControlRequest(cdr_payload) -> SimControlRequest:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = SimControlRequest()
    return cdr_body_to_py_SimControlRequest(reader, dst)
