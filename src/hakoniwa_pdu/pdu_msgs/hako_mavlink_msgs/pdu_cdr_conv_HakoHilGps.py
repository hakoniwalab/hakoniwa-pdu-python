from .pdu_pytype_HakoHilGps import HakoHilGps
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_HakoHilGps(writer: CdrWriter, src: HakoHilGps):
    writer.write_uint64(src.time_usec)
    writer.write_int32(src.lat)
    writer.write_int32(src.lon)
    writer.write_int32(src.alt)
    writer.write_uint16(src.eph)
    writer.write_uint16(src.epv)
    writer.write_uint16(src.vel)
    writer.write_int16(src.vn)
    writer.write_int16(src.ve)
    writer.write_int16(src.vd)
    writer.write_uint16(src.cog)
    writer.write_uint8(src.satellites_visible)
    writer.write_uint8(src.id)
    writer.write_uint8(src.yaw)
    writer.write_uint8(src.fix_type)


def cdr_body_to_py_HakoHilGps(reader: CdrReader, dst: HakoHilGps):
    dst.time_usec = reader.read_uint64()
    dst.lat = reader.read_int32()
    dst.lon = reader.read_int32()
    dst.alt = reader.read_int32()
    dst.eph = reader.read_uint16()
    dst.epv = reader.read_uint16()
    dst.vel = reader.read_uint16()
    dst.vn = reader.read_int16()
    dst.ve = reader.read_int16()
    dst.vd = reader.read_int16()
    dst.cog = reader.read_uint16()
    dst.satellites_visible = reader.read_uint8()
    dst.id = reader.read_uint8()
    dst.yaw = reader.read_uint8()
    dst.fix_type = reader.read_uint8()
    return dst


def py_to_cdr_HakoHilGps(src: HakoHilGps) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_HakoHilGps(writer, src)
    return writer.bytes()


def cdr_to_py_HakoHilGps(cdr_payload) -> HakoHilGps:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = HakoHilGps()
    return cdr_body_to_py_HakoHilGps(reader, dst)
