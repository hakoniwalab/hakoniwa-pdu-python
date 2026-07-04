from .pdu_pytype_HakoATTITUDE import HakoATTITUDE
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_HakoATTITUDE(writer: CdrWriter, src: HakoATTITUDE):
    writer.write_uint32(src.time_boot_ms)
    writer.write_float32(src.roll)
    writer.write_float32(src.pitch)
    writer.write_float32(src.yaw)
    writer.write_float32(src.rollspeed)
    writer.write_float32(src.pitchspeed)
    writer.write_float32(src.yawspeed)


def cdr_body_to_py_HakoATTITUDE(reader: CdrReader, dst: HakoATTITUDE):
    dst.time_boot_ms = reader.read_uint32()
    dst.roll = reader.read_float32()
    dst.pitch = reader.read_float32()
    dst.yaw = reader.read_float32()
    dst.rollspeed = reader.read_float32()
    dst.pitchspeed = reader.read_float32()
    dst.yawspeed = reader.read_float32()
    return dst


def py_to_cdr_HakoATTITUDE(src: HakoATTITUDE) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_HakoATTITUDE(writer, src)
    return writer.bytes()


def cdr_to_py_HakoATTITUDE(cdr_payload) -> HakoATTITUDE:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = HakoATTITUDE()
    return cdr_body_to_py_HakoATTITUDE(reader, dst)
