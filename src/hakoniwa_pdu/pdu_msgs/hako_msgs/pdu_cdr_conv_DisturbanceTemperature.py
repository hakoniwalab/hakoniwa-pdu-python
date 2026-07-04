from .pdu_pytype_DisturbanceTemperature import DisturbanceTemperature
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_DisturbanceTemperature(writer: CdrWriter, src: DisturbanceTemperature):
    writer.write_float64(src.value)


def cdr_body_to_py_DisturbanceTemperature(reader: CdrReader, dst: DisturbanceTemperature):
    dst.value = reader.read_float64()
    return dst


def py_to_cdr_DisturbanceTemperature(src: DisturbanceTemperature) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_DisturbanceTemperature(writer, src)
    return writer.bytes()


def cdr_to_py_DisturbanceTemperature(cdr_payload) -> DisturbanceTemperature:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = DisturbanceTemperature()
    return cdr_body_to_py_DisturbanceTemperature(reader, dst)
