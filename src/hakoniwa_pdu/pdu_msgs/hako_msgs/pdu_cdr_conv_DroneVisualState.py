from .pdu_pytype_DroneVisualState import DroneVisualState
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_DroneVisualState(writer: CdrWriter, src: DroneVisualState):
    writer.write_float32(src.x)
    writer.write_float32(src.y)
    writer.write_float32(src.z)
    writer.write_float32(src.roll)
    writer.write_float32(src.pitch)
    writer.write_float32(src.yaw)
    writer.write_sequence_length(src.pwm_duty)
    for elem in src.pwm_duty:
        writer.write_float32(elem)


def cdr_body_to_py_DroneVisualState(reader: CdrReader, dst: DroneVisualState):
    dst.x = reader.read_float32()
    dst.y = reader.read_float32()
    dst.z = reader.read_float32()
    dst.roll = reader.read_float32()
    dst.pitch = reader.read_float32()
    dst.yaw = reader.read_float32()
    dst.pwm_duty = [reader.read_float32() for _ in range(reader.read_uint32())]
    return dst


def py_to_cdr_DroneVisualState(src: DroneVisualState) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_DroneVisualState(writer, src)
    return writer.bytes()


def cdr_to_py_DroneVisualState(cdr_payload) -> DroneVisualState:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = DroneVisualState()
    return cdr_body_to_py_DroneVisualState(reader, dst)
