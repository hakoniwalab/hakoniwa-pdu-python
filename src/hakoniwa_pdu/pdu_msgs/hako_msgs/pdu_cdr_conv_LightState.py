from .pdu_pytype_LightState import LightState
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_LightState(writer: CdrWriter, src: LightState):
    writer.write_string(src.source)
    writer.write_uint8(src.mode)
    writer.write_float64(src.luminous_intensity_scale)
    writer.write_bool(src.is_lit)


def cdr_body_to_py_LightState(reader: CdrReader, dst: LightState):
    dst.source = reader.read_string()
    dst.mode = reader.read_uint8()
    dst.luminous_intensity_scale = reader.read_float64()
    dst.is_lit = reader.read_bool()
    return dst


def py_to_cdr_LightState(src: LightState) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_LightState(writer, src)
    return writer.bytes()


def cdr_to_py_LightState(cdr_payload) -> LightState:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = LightState()
    return cdr_body_to_py_LightState(reader, dst)
