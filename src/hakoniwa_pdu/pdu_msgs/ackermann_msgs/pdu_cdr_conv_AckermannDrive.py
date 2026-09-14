from .pdu_pytype_AckermannDrive import AckermannDrive
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_AckermannDrive(writer: CdrWriter, src: AckermannDrive):
    writer.write_float32(src.steering_angle)
    writer.write_float32(src.steering_angle_velocity)
    writer.write_float32(src.speed)
    writer.write_float32(src.acceleration)
    writer.write_float32(src.jerk)


def cdr_body_to_py_AckermannDrive(reader: CdrReader, dst: AckermannDrive):
    dst.steering_angle = reader.read_float32()
    dst.steering_angle_velocity = reader.read_float32()
    dst.speed = reader.read_float32()
    dst.acceleration = reader.read_float32()
    dst.jerk = reader.read_float32()
    return dst


def py_to_cdr_AckermannDrive(src: AckermannDrive) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_AckermannDrive(writer, src)
    return writer.bytes()


def cdr_to_py_AckermannDrive(cdr_payload) -> AckermannDrive:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = AckermannDrive()
    return cdr_body_to_py_AckermannDrive(reader, dst)
