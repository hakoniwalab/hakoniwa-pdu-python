from .pdu_pytype_MultiEchoLaserScan import MultiEchoLaserScan
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_Header import *
from ..sensor_msgs.pdu_cdr_conv_LaserEcho import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *



def py_to_cdr_body_MultiEchoLaserScan(writer: CdrWriter, src: MultiEchoLaserScan):
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
        py_to_cdr_body_LaserEcho(writer, elem)
    writer.write_sequence_length(src.intensities)
    for elem in src.intensities:
        py_to_cdr_body_LaserEcho(writer, elem)


def cdr_body_to_py_MultiEchoLaserScan(reader: CdrReader, dst: MultiEchoLaserScan):
    cdr_body_to_py_Header(reader, dst.header)
    dst.angle_min = reader.read_float32()
    dst.angle_max = reader.read_float32()
    dst.angle_increment = reader.read_float32()
    dst.time_increment = reader.read_float32()
    dst.scan_time = reader.read_float32()
    dst.range_min = reader.read_float32()
    dst.range_max = reader.read_float32()
    dst.ranges = []
    for _ in range(reader.read_uint32()):
        elem = LaserEcho()
        cdr_body_to_py_LaserEcho(reader, elem)
        dst.ranges.append(elem)
    dst.intensities = []
    for _ in range(reader.read_uint32()):
        elem = LaserEcho()
        cdr_body_to_py_LaserEcho(reader, elem)
        dst.intensities.append(elem)
    return dst


def py_to_cdr_MultiEchoLaserScan(src: MultiEchoLaserScan) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_MultiEchoLaserScan(writer, src)
    return writer.bytes()


def cdr_to_py_MultiEchoLaserScan(cdr_payload) -> MultiEchoLaserScan:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = MultiEchoLaserScan()
    return cdr_body_to_py_MultiEchoLaserScan(reader, dst)
