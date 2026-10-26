from .pdu_pytype_SetLightResponse import SetLightResponse
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_SetLightResponse(writer: CdrWriter, src: SetLightResponse):
    writer.write_uint32(src.result_code)
    writer.write_string(src.message)


def cdr_body_to_py_SetLightResponse(reader: CdrReader, dst: SetLightResponse):
    dst.result_code = reader.read_uint32()
    dst.message = reader.read_string()
    return dst


def py_to_cdr_SetLightResponse(src: SetLightResponse) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_SetLightResponse(writer, src)
    return writer.bytes()


def cdr_to_py_SetLightResponse(cdr_payload) -> SetLightResponse:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = SetLightResponse()
    return cdr_body_to_py_SetLightResponse(reader, dst)
