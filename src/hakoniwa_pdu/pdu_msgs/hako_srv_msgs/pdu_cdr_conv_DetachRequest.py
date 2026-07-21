from .pdu_pytype_DetachRequest import DetachRequest
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_DetachRequest(writer: CdrWriter, src: DetachRequest):
    writer.write_uint64(src.session_id)


def cdr_body_to_py_DetachRequest(reader: CdrReader, dst: DetachRequest):
    dst.session_id = reader.read_uint64()
    return dst


def py_to_cdr_DetachRequest(src: DetachRequest) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_DetachRequest(writer, src)
    return writer.bytes()


def cdr_to_py_DetachRequest(cdr_payload) -> DetachRequest:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = DetachRequest()
    return cdr_body_to_py_DetachRequest(reader, dst)
