from .pdu_pytype_CameraCaptureImageResponse import CameraCaptureImageResponse
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_CameraCaptureImageResponse(writer: CdrWriter, src: CameraCaptureImageResponse):
    writer.write_bool(src.ok)
    writer.write_sequence_length(src.data)
    for elem in src.data:
        writer.write_uint8(elem)
    writer.write_string(src.message)


def cdr_body_to_py_CameraCaptureImageResponse(reader: CdrReader, dst: CameraCaptureImageResponse):
    dst.ok = reader.read_bool()
    dst.data = [reader.read_uint8() for _ in range(reader.read_uint32())]
    dst.message = reader.read_string()
    return dst


def py_to_cdr_CameraCaptureImageResponse(src: CameraCaptureImageResponse) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_CameraCaptureImageResponse(writer, src)
    return writer.bytes()


def cdr_to_py_CameraCaptureImageResponse(cdr_payload) -> CameraCaptureImageResponse:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = CameraCaptureImageResponse()
    return cdr_body_to_py_CameraCaptureImageResponse(reader, dst)
