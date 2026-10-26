from .pdu_pytype_SetLightRequest import SetLightRequest
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_SetLightRequest(writer: CdrWriter, src: SetLightRequest):
    writer.write_string(src.source)
    writer.write_uint8(src.mode)
    writer.write_float64(src.luminous_intensity_scale)
    writer.write_float64(src.flashing_on_s)
    writer.write_float64(src.flashing_off_s)
    writer.write_float64(src.transition_s)


def cdr_body_to_py_SetLightRequest(reader: CdrReader, dst: SetLightRequest):
    dst.source = reader.read_string()
    dst.mode = reader.read_uint8()
    dst.luminous_intensity_scale = reader.read_float64()
    dst.flashing_on_s = reader.read_float64()
    dst.flashing_off_s = reader.read_float64()
    dst.transition_s = reader.read_float64()
    return dst


def py_to_cdr_SetLightRequest(src: SetLightRequest) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_SetLightRequest(writer, src)
    return writer.bytes()


def cdr_to_py_SetLightRequest(cdr_payload) -> SetLightRequest:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = SetLightRequest()
    return cdr_body_to_py_SetLightRequest(reader, dst)
