from .pdu_pytype_DetachResponse import DetachResponse
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_DetachResponse(writer: CdrWriter, src: DetachResponse):
    writer.write_uint32(src.result_code)


def cdr_body_to_py_DetachResponse(reader: CdrReader, dst: DetachResponse):
    dst.result_code = reader.read_uint32()
    return dst


def py_to_cdr_DetachResponse(src: DetachResponse) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_DetachResponse(writer, src)
    return writer.bytes()


def cdr_to_py_DetachResponse(cdr_payload) -> DetachResponse:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = DetachResponse()
    return cdr_body_to_py_DetachResponse(reader, dst)
