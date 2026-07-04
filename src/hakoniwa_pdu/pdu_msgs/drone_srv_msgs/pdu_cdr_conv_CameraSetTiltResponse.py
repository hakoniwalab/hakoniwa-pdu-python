from .pdu_pytype_CameraSetTiltResponse import CameraSetTiltResponse
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_CameraSetTiltResponse(writer: CdrWriter, src: CameraSetTiltResponse):
    writer.write_bool(src.ok)
    writer.write_string(src.message)


def cdr_body_to_py_CameraSetTiltResponse(reader: CdrReader, dst: CameraSetTiltResponse):
    dst.ok = reader.read_bool()
    dst.message = reader.read_string()
    return dst


def py_to_cdr_CameraSetTiltResponse(src: CameraSetTiltResponse) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_CameraSetTiltResponse(writer, src)
    return writer.bytes()


def cdr_to_py_CameraSetTiltResponse(cdr_payload) -> CameraSetTiltResponse:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = CameraSetTiltResponse()
    return cdr_body_to_py_CameraSetTiltResponse(reader, dst)
