from .pdu_pytype_HakoHilStateQuaternion import HakoHilStateQuaternion
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_HakoHilStateQuaternion(writer: CdrWriter, src: HakoHilStateQuaternion):
    writer.write_uint64(src.time_usec)
    values = src.attitude_quaternion
    for i in range(4):
        writer.write_float32(values[i] if i < len(values) else 0.0)
    writer.write_float32(src.rollspeed)
    writer.write_float32(src.pitchspeed)
    writer.write_float32(src.yawspeed)
    writer.write_int32(src.lat)
    writer.write_int32(src.lon)
    writer.write_int32(src.alt)
    writer.write_int16(src.vx)
    writer.write_int16(src.vy)
    writer.write_int16(src.vz)
    writer.write_uint16(src.ind_airspeed)
    writer.write_uint16(src.true_airspeed)
    writer.write_int16(src.xacc)
    writer.write_int16(src.yacc)
    writer.write_int16(src.zacc)


def cdr_body_to_py_HakoHilStateQuaternion(reader: CdrReader, dst: HakoHilStateQuaternion):
    dst.time_usec = reader.read_uint64()
    dst.attitude_quaternion = [reader.read_float32() for _ in range(4)]
    dst.rollspeed = reader.read_float32()
    dst.pitchspeed = reader.read_float32()
    dst.yawspeed = reader.read_float32()
    dst.lat = reader.read_int32()
    dst.lon = reader.read_int32()
    dst.alt = reader.read_int32()
    dst.vx = reader.read_int16()
    dst.vy = reader.read_int16()
    dst.vz = reader.read_int16()
    dst.ind_airspeed = reader.read_uint16()
    dst.true_airspeed = reader.read_uint16()
    dst.xacc = reader.read_int16()
    dst.yacc = reader.read_int16()
    dst.zacc = reader.read_int16()
    return dst


def py_to_cdr_HakoHilStateQuaternion(src: HakoHilStateQuaternion) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_HakoHilStateQuaternion(writer, src)
    return writer.bytes()


def cdr_to_py_HakoHilStateQuaternion(cdr_payload) -> HakoHilStateQuaternion:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = HakoHilStateQuaternion()
    return cdr_body_to_py_HakoHilStateQuaternion(reader, dst)
