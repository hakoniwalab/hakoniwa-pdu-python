from .pdu_pytype_PointCloud import PointCloud
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..sensor_msgs.pdu_cdr_conv_ChannelFloat32 import *
from ..std_msgs.pdu_cdr_conv_Header import *
from ..geometry_msgs.pdu_cdr_conv_Point32 import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *



def py_to_cdr_body_PointCloud(writer: CdrWriter, src: PointCloud):
    py_to_cdr_body_Header(writer, src.header)
    writer.write_sequence_length(src.points)
    for elem in src.points:
        py_to_cdr_body_Point32(writer, elem)
    writer.write_sequence_length(src.channels)
    for elem in src.channels:
        py_to_cdr_body_ChannelFloat32(writer, elem)


def cdr_body_to_py_PointCloud(reader: CdrReader, dst: PointCloud):
    cdr_body_to_py_Header(reader, dst.header)
    dst.points = []
    for _ in range(reader.read_uint32()):
        elem = Point32()
        cdr_body_to_py_Point32(reader, elem)
        dst.points.append(elem)
    dst.channels = []
    for _ in range(reader.read_uint32()):
        elem = ChannelFloat32()
        cdr_body_to_py_ChannelFloat32(reader, elem)
        dst.channels.append(elem)
    return dst


def py_to_cdr_PointCloud(src: PointCloud) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_PointCloud(writer, src)
    return writer.bytes()


def cdr_to_py_PointCloud(cdr_payload) -> PointCloud:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = PointCloud()
    return cdr_body_to_py_PointCloud(reader, dst)
