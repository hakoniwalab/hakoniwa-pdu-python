from .pdu_pytype_Imu import Imu
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_Header import *
from ..geometry_msgs.pdu_cdr_conv_Quaternion import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *
from ..geometry_msgs.pdu_cdr_conv_Vector3 import *



def py_to_cdr_body_Imu(writer: CdrWriter, src: Imu):
    py_to_cdr_body_Header(writer, src.header)
    py_to_cdr_body_Quaternion(writer, src.orientation)
    values = src.orientation_covariance
    for i in range(9):
        writer.write_float64(values[i] if i < len(values) else 0.0)
    py_to_cdr_body_Vector3(writer, src.angular_velocity)
    values = src.angular_velocity_covariance
    for i in range(9):
        writer.write_float64(values[i] if i < len(values) else 0.0)
    py_to_cdr_body_Vector3(writer, src.linear_acceleration)
    values = src.linear_acceleration_covariance
    for i in range(9):
        writer.write_float64(values[i] if i < len(values) else 0.0)


def cdr_body_to_py_Imu(reader: CdrReader, dst: Imu):
    cdr_body_to_py_Header(reader, dst.header)
    cdr_body_to_py_Quaternion(reader, dst.orientation)
    dst.orientation_covariance = [reader.read_float64() for _ in range(9)]
    cdr_body_to_py_Vector3(reader, dst.angular_velocity)
    dst.angular_velocity_covariance = [reader.read_float64() for _ in range(9)]
    cdr_body_to_py_Vector3(reader, dst.linear_acceleration)
    dst.linear_acceleration_covariance = [reader.read_float64() for _ in range(9)]
    return dst


def py_to_cdr_Imu(src: Imu) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_Imu(writer, src)
    return writer.bytes()


def cdr_to_py_Imu(cdr_payload) -> Imu:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = Imu()
    return cdr_body_to_py_Imu(reader, dst)
