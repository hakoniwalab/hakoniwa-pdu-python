from .pdu_pytype_DroneLandResponse import DroneLandResponse
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_DroneLandResponse(writer: CdrWriter, src: DroneLandResponse):
    writer.write_bool(src.ok)
    writer.write_string(src.message)


def cdr_body_to_py_DroneLandResponse(reader: CdrReader, dst: DroneLandResponse):
    dst.ok = reader.read_bool()
    dst.message = reader.read_string()
    return dst


def py_to_cdr_DroneLandResponse(src: DroneLandResponse) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_DroneLandResponse(writer, src)
    return writer.bytes()


def cdr_to_py_DroneLandResponse(cdr_payload) -> DroneLandResponse:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = DroneLandResponse()
    return cdr_body_to_py_DroneLandResponse(reader, dst)
