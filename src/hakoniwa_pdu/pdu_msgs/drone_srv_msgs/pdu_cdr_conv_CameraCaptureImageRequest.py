from .pdu_pytype_CameraCaptureImageRequest import CameraCaptureImageRequest
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_CameraCaptureImageRequest(writer: CdrWriter, src: CameraCaptureImageRequest):
    writer.write_string(src.drone_name)
    writer.write_string(src.image_type)


def cdr_body_to_py_CameraCaptureImageRequest(reader: CdrReader, dst: CameraCaptureImageRequest):
    dst.drone_name = reader.read_string()
    dst.image_type = reader.read_string()
    return dst


def py_to_cdr_CameraCaptureImageRequest(src: CameraCaptureImageRequest) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_CameraCaptureImageRequest(writer, src)
    return writer.bytes()


def cdr_to_py_CameraCaptureImageRequest(cdr_payload) -> CameraCaptureImageRequest:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = CameraCaptureImageRequest()
    return cdr_body_to_py_CameraCaptureImageRequest(reader, dst)
