from .pdu_pytype_HakoHeartbeat import HakoHeartbeat
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_HakoHeartbeat(writer: CdrWriter, src: HakoHeartbeat):
    writer.write_uint8(src.type)
    writer.write_uint8(src.autopilot)
    writer.write_uint8(src.base_mode)
    writer.write_uint32(src.custom_mode)
    writer.write_uint8(src.system_status)
    writer.write_uint8(src.mavlink_version)


def cdr_body_to_py_HakoHeartbeat(reader: CdrReader, dst: HakoHeartbeat):
    dst.type = reader.read_uint8()
    dst.autopilot = reader.read_uint8()
    dst.base_mode = reader.read_uint8()
    dst.custom_mode = reader.read_uint32()
    dst.system_status = reader.read_uint8()
    dst.mavlink_version = reader.read_uint8()
    return dst


def py_to_cdr_HakoHeartbeat(src: HakoHeartbeat) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_HakoHeartbeat(writer, src)
    return writer.bytes()


def cdr_to_py_HakoHeartbeat(cdr_payload) -> HakoHeartbeat:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = HakoHeartbeat()
    return cdr_body_to_py_HakoHeartbeat(reader, dst)
