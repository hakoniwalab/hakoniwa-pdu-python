from .pdu_pytype_GlobalPositionTarget import GlobalPositionTarget
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_Header import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *
from ..geometry_msgs.pdu_cdr_conv_Vector3 import *



def py_to_cdr_body_GlobalPositionTarget(writer: CdrWriter, src: GlobalPositionTarget):
    py_to_cdr_body_Header(writer, src.header)
    writer.write_uint8(src.coordinate_frame)
    writer.write_uint16(src.type_mask)
    writer.write_float64(src.latitude)
    writer.write_float64(src.longitude)
    writer.write_float32(src.altitude)
    py_to_cdr_body_Vector3(writer, src.velocity)
    py_to_cdr_body_Vector3(writer, src.acceleration_or_force)
    writer.write_float32(src.yaw)
    writer.write_float32(src.yaw_rate)


def cdr_body_to_py_GlobalPositionTarget(reader: CdrReader, dst: GlobalPositionTarget):
    cdr_body_to_py_Header(reader, dst.header)
    dst.coordinate_frame = reader.read_uint8()
    dst.type_mask = reader.read_uint16()
    dst.latitude = reader.read_float64()
    dst.longitude = reader.read_float64()
    dst.altitude = reader.read_float32()
    cdr_body_to_py_Vector3(reader, dst.velocity)
    cdr_body_to_py_Vector3(reader, dst.acceleration_or_force)
    dst.yaw = reader.read_float32()
    dst.yaw_rate = reader.read_float32()
    return dst


def py_to_cdr_GlobalPositionTarget(src: GlobalPositionTarget) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_GlobalPositionTarget(writer, src)
    return writer.bytes()


def cdr_to_py_GlobalPositionTarget(cdr_payload) -> GlobalPositionTarget:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = GlobalPositionTarget()
    return cdr_body_to_py_GlobalPositionTarget(reader, dst)
