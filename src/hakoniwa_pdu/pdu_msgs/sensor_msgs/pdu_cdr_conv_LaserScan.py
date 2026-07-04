from .pdu_pytype_LaserScan import LaserScan
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_Header import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *



def py_to_cdr_body_LaserScan(writer: CdrWriter, src: LaserScan):
    py_to_cdr_body_Header(writer, src.header)
    writer.write_float32(src.angle_min)
    writer.write_float32(src.angle_max)
    writer.write_float32(src.angle_increment)
    writer.write_float32(src.time_increment)
    writer.write_float32(src.scan_time)
    writer.write_float32(src.range_min)
    writer.write_float32(src.range_max)
    writer.write_sequence_length(src.ranges)
    for elem in src.ranges:
        writer.write_float32(elem)
    writer.write_sequence_length(src.intensities)
    for elem in src.intensities:
        writer.write_float32(elem)


def cdr_body_to_py_LaserScan(reader: CdrReader, dst: LaserScan):
    cdr_body_to_py_Header(reader, dst.header)
    dst.angle_min = reader.read_float32()
    dst.angle_max = reader.read_float32()
    dst.angle_increment = reader.read_float32()
    dst.time_increment = reader.read_float32()
    dst.scan_time = reader.read_float32()
    dst.range_min = reader.read_float32()
    dst.range_max = reader.read_float32()
    dst.ranges = [reader.read_float32() for _ in range(reader.read_uint32())]
    dst.intensities = [reader.read_float32() for _ in range(reader.read_uint32())]
    return dst


def py_to_cdr_LaserScan(src: LaserScan) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_LaserScan(writer, src)
    return writer.bytes()


def cdr_to_py_LaserScan(cdr_payload) -> LaserScan:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = LaserScan()
    return cdr_body_to_py_LaserScan(reader, dst)
