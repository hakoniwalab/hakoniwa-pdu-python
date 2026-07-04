from .pdu_pytype_Ev3PduActuatorHeader import Ev3PduActuatorHeader
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_Ev3PduActuatorHeader(writer: CdrWriter, src: Ev3PduActuatorHeader):
    writer.write_string(src.name)
    writer.write_uint32(src.version)
    writer.write_int64(src.asset_time)
    writer.write_uint32(src.ext_off)
    writer.write_uint32(src.ext_size)


def cdr_body_to_py_Ev3PduActuatorHeader(reader: CdrReader, dst: Ev3PduActuatorHeader):
    dst.name = reader.read_string()
    dst.version = reader.read_uint32()
    dst.asset_time = reader.read_int64()
    dst.ext_off = reader.read_uint32()
    dst.ext_size = reader.read_uint32()
    return dst


def py_to_cdr_Ev3PduActuatorHeader(src: Ev3PduActuatorHeader) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_Ev3PduActuatorHeader(writer, src)
    return writer.bytes()


def cdr_to_py_Ev3PduActuatorHeader(cdr_payload) -> Ev3PduActuatorHeader:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = Ev3PduActuatorHeader()
    return cdr_body_to_py_Ev3PduActuatorHeader(reader, dst)
