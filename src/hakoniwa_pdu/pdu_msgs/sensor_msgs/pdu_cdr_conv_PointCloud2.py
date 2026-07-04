from .pdu_pytype_PointCloud2 import PointCloud2
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_Header import *
from ..sensor_msgs.pdu_cdr_conv_PointField import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *



def py_to_cdr_body_PointCloud2(writer: CdrWriter, src: PointCloud2):
    py_to_cdr_body_Header(writer, src.header)
    writer.write_uint32(src.height)
    writer.write_uint32(src.width)
    writer.write_sequence_length(src.fields)
    for elem in src.fields:
        py_to_cdr_body_PointField(writer, elem)
    writer.write_bool(src.is_bigendian)
    writer.write_uint32(src.point_step)
    writer.write_uint32(src.row_step)
    writer.write_sequence_length(src.data)
    for elem in src.data:
        writer.write_uint8(elem)
    writer.write_bool(src.is_dense)


def cdr_body_to_py_PointCloud2(reader: CdrReader, dst: PointCloud2):
    cdr_body_to_py_Header(reader, dst.header)
    dst.height = reader.read_uint32()
    dst.width = reader.read_uint32()
    dst.fields = []
    for _ in range(reader.read_uint32()):
        elem = PointField()
        cdr_body_to_py_PointField(reader, elem)
        dst.fields.append(elem)
    dst.is_bigendian = reader.read_bool()
    dst.point_step = reader.read_uint32()
    dst.row_step = reader.read_uint32()
    dst.data = [reader.read_uint8() for _ in range(reader.read_uint32())]
    dst.is_dense = reader.read_bool()
    return dst


def py_to_cdr_PointCloud2(src: PointCloud2) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_PointCloud2(writer, src)
    return writer.bytes()


def cdr_to_py_PointCloud2(cdr_payload) -> PointCloud2:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = PointCloud2()
    return cdr_body_to_py_PointCloud2(reader, dst)
