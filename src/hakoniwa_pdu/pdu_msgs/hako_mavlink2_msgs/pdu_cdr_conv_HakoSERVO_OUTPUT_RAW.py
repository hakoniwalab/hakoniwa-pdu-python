from .pdu_pytype_HakoSERVO_OUTPUT_RAW import HakoSERVO_OUTPUT_RAW
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_HakoSERVO_OUTPUT_RAW(writer: CdrWriter, src: HakoSERVO_OUTPUT_RAW):
    writer.write_uint32(src.time_usec)
    writer.write_uint8(src.port)
    writer.write_uint16(src.servo1_raw)
    writer.write_uint16(src.servo2_raw)
    writer.write_uint16(src.servo3_raw)
    writer.write_uint16(src.servo4_raw)
    writer.write_uint16(src.servo5_raw)
    writer.write_uint16(src.servo6_raw)
    writer.write_uint16(src.servo7_raw)
    writer.write_uint16(src.servo8_raw)
    writer.write_uint16(src.servo9_raw)
    writer.write_uint16(src.servo10_raw)
    writer.write_uint16(src.servo11_raw)
    writer.write_uint16(src.servo12_raw)
    writer.write_uint16(src.servo13_raw)
    writer.write_uint16(src.servo14_raw)
    writer.write_uint16(src.servo15_raw)
    writer.write_uint16(src.servo16_raw)


def cdr_body_to_py_HakoSERVO_OUTPUT_RAW(reader: CdrReader, dst: HakoSERVO_OUTPUT_RAW):
    dst.time_usec = reader.read_uint32()
    dst.port = reader.read_uint8()
    dst.servo1_raw = reader.read_uint16()
    dst.servo2_raw = reader.read_uint16()
    dst.servo3_raw = reader.read_uint16()
    dst.servo4_raw = reader.read_uint16()
    dst.servo5_raw = reader.read_uint16()
    dst.servo6_raw = reader.read_uint16()
    dst.servo7_raw = reader.read_uint16()
    dst.servo8_raw = reader.read_uint16()
    dst.servo9_raw = reader.read_uint16()
    dst.servo10_raw = reader.read_uint16()
    dst.servo11_raw = reader.read_uint16()
    dst.servo12_raw = reader.read_uint16()
    dst.servo13_raw = reader.read_uint16()
    dst.servo14_raw = reader.read_uint16()
    dst.servo15_raw = reader.read_uint16()
    dst.servo16_raw = reader.read_uint16()
    return dst


def py_to_cdr_HakoSERVO_OUTPUT_RAW(src: HakoSERVO_OUTPUT_RAW) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_HakoSERVO_OUTPUT_RAW(writer, src)
    return writer.bytes()


def cdr_to_py_HakoSERVO_OUTPUT_RAW(cdr_payload) -> HakoSERVO_OUTPUT_RAW:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = HakoSERVO_OUTPUT_RAW()
    return cdr_body_to_py_HakoSERVO_OUTPUT_RAW(reader, dst)
