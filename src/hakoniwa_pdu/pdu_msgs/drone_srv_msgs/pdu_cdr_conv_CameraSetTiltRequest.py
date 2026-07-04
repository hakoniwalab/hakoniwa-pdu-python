from .pdu_pytype_CameraSetTiltRequest import CameraSetTiltRequest
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_CameraSetTiltRequest(writer: CdrWriter, src: CameraSetTiltRequest):
    writer.write_string(src.drone_name)
    writer.write_float32(src.tilt_angle_deg)


def cdr_body_to_py_CameraSetTiltRequest(reader: CdrReader, dst: CameraSetTiltRequest):
    dst.drone_name = reader.read_string()
    dst.tilt_angle_deg = reader.read_float32()
    return dst


def py_to_cdr_CameraSetTiltRequest(src: CameraSetTiltRequest) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_CameraSetTiltRequest(writer, src)
    return writer.bytes()


def cdr_to_py_CameraSetTiltRequest(cdr_payload) -> CameraSetTiltRequest:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = CameraSetTiltRequest()
    return cdr_body_to_py_CameraSetTiltRequest(reader, dst)
