from .pdu_pytype_HakoHilSensor import HakoHilSensor
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_HakoHilSensor(writer: CdrWriter, src: HakoHilSensor):
    writer.write_uint64(src.time_usec)
    writer.write_float32(src.xacc)
    writer.write_float32(src.yacc)
    writer.write_float32(src.zacc)
    writer.write_float32(src.xgyro)
    writer.write_float32(src.ygyro)
    writer.write_float32(src.zgyro)
    writer.write_float32(src.xmag)
    writer.write_float32(src.ymag)
    writer.write_float32(src.zmag)
    writer.write_float32(src.abs_pressure)
    writer.write_float32(src.diff_pressure)
    writer.write_float32(src.pressure_alt)
    writer.write_float32(src.temperature)
    writer.write_uint32(src.fields_updated)
    writer.write_uint8(src.id)


def cdr_body_to_py_HakoHilSensor(reader: CdrReader, dst: HakoHilSensor):
    dst.time_usec = reader.read_uint64()
    dst.xacc = reader.read_float32()
    dst.yacc = reader.read_float32()
    dst.zacc = reader.read_float32()
    dst.xgyro = reader.read_float32()
    dst.ygyro = reader.read_float32()
    dst.zgyro = reader.read_float32()
    dst.xmag = reader.read_float32()
    dst.ymag = reader.read_float32()
    dst.zmag = reader.read_float32()
    dst.abs_pressure = reader.read_float32()
    dst.diff_pressure = reader.read_float32()
    dst.pressure_alt = reader.read_float32()
    dst.temperature = reader.read_float32()
    dst.fields_updated = reader.read_uint32()
    dst.id = reader.read_uint8()
    return dst


def py_to_cdr_HakoHilSensor(src: HakoHilSensor) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_HakoHilSensor(writer, src)
    return writer.bytes()


def cdr_to_py_HakoHilSensor(cdr_payload) -> HakoHilSensor:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = HakoHilSensor()
    return cdr_body_to_py_HakoHilSensor(reader, dst)
