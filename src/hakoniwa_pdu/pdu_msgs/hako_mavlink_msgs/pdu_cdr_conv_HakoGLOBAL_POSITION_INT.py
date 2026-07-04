from .pdu_pytype_HakoGLOBAL_POSITION_INT import HakoGLOBAL_POSITION_INT
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_HakoGLOBAL_POSITION_INT(writer: CdrWriter, src: HakoGLOBAL_POSITION_INT):
    writer.write_uint32(src.time_boot_ms)
    writer.write_int32(src.lat)
    writer.write_int32(src.lon)
    writer.write_int32(src.alt)
    writer.write_int32(src.relative_alt)
    writer.write_int16(src.vx)
    writer.write_int16(src.vy)
    writer.write_int16(src.vz)
    writer.write_uint16(src.hdg)


def cdr_body_to_py_HakoGLOBAL_POSITION_INT(reader: CdrReader, dst: HakoGLOBAL_POSITION_INT):
    dst.time_boot_ms = reader.read_uint32()
    dst.lat = reader.read_int32()
    dst.lon = reader.read_int32()
    dst.alt = reader.read_int32()
    dst.relative_alt = reader.read_int32()
    dst.vx = reader.read_int16()
    dst.vy = reader.read_int16()
    dst.vz = reader.read_int16()
    dst.hdg = reader.read_uint16()
    return dst


def py_to_cdr_HakoGLOBAL_POSITION_INT(src: HakoGLOBAL_POSITION_INT) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_HakoGLOBAL_POSITION_INT(writer, src)
    return writer.bytes()


def cdr_to_py_HakoGLOBAL_POSITION_INT(cdr_payload) -> HakoGLOBAL_POSITION_INT:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = HakoGLOBAL_POSITION_INT()
    return cdr_body_to_py_HakoGLOBAL_POSITION_INT(reader, dst)
