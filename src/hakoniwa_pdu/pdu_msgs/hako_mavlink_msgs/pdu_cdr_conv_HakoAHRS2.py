from .pdu_pytype_HakoAHRS2 import HakoAHRS2
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_HakoAHRS2(writer: CdrWriter, src: HakoAHRS2):
    writer.write_float32(src.roll)
    writer.write_float32(src.pitch)
    writer.write_float32(src.yaw)
    writer.write_float32(src.altitude)
    writer.write_int32(src.lat)
    writer.write_int32(src.lng)


def cdr_body_to_py_HakoAHRS2(reader: CdrReader, dst: HakoAHRS2):
    dst.roll = reader.read_float32()
    dst.pitch = reader.read_float32()
    dst.yaw = reader.read_float32()
    dst.altitude = reader.read_float32()
    dst.lat = reader.read_int32()
    dst.lng = reader.read_int32()
    return dst


def py_to_cdr_HakoAHRS2(src: HakoAHRS2) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_HakoAHRS2(writer, src)
    return writer.bytes()


def cdr_to_py_HakoAHRS2(cdr_payload) -> HakoAHRS2:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = HakoAHRS2()
    return cdr_body_to_py_HakoAHRS2(reader, dst)
