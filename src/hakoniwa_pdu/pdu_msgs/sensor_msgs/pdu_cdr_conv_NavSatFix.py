from .pdu_pytype_NavSatFix import NavSatFix
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_Header import *
from ..sensor_msgs.pdu_cdr_conv_NavSatStatus import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *



def py_to_cdr_body_NavSatFix(writer: CdrWriter, src: NavSatFix):
    py_to_cdr_body_Header(writer, src.header)
    py_to_cdr_body_NavSatStatus(writer, src.status)
    writer.write_float64(src.latitude)
    writer.write_float64(src.longitude)
    writer.write_float64(src.altitude)
    values = src.position_covariance
    for i in range(9):
        writer.write_float64(values[i] if i < len(values) else 0.0)
    writer.write_uint8(src.position_covariance_type)


def cdr_body_to_py_NavSatFix(reader: CdrReader, dst: NavSatFix):
    cdr_body_to_py_Header(reader, dst.header)
    cdr_body_to_py_NavSatStatus(reader, dst.status)
    dst.latitude = reader.read_float64()
    dst.longitude = reader.read_float64()
    dst.altitude = reader.read_float64()
    dst.position_covariance = [reader.read_float64() for _ in range(9)]
    dst.position_covariance_type = reader.read_uint8()
    return dst


def py_to_cdr_NavSatFix(src: NavSatFix) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_NavSatFix(writer, src)
    return writer.bytes()


def cdr_to_py_NavSatFix(cdr_payload) -> NavSatFix:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = NavSatFix()
    return cdr_body_to_py_NavSatFix(reader, dst)
