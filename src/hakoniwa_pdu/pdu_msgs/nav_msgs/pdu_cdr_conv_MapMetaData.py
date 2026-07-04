from .pdu_pytype_MapMetaData import MapMetaData
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..geometry_msgs.pdu_cdr_conv_Point import *
from ..geometry_msgs.pdu_cdr_conv_Pose import *
from ..geometry_msgs.pdu_cdr_conv_Quaternion import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *



def py_to_cdr_body_MapMetaData(writer: CdrWriter, src: MapMetaData):
    py_to_cdr_body_Time(writer, src.map_load_time)
    writer.write_float32(src.resolution)
    writer.write_uint32(src.width)
    writer.write_uint32(src.height)
    py_to_cdr_body_Pose(writer, src.origin)


def cdr_body_to_py_MapMetaData(reader: CdrReader, dst: MapMetaData):
    cdr_body_to_py_Time(reader, dst.map_load_time)
    dst.resolution = reader.read_float32()
    dst.width = reader.read_uint32()
    dst.height = reader.read_uint32()
    cdr_body_to_py_Pose(reader, dst.origin)
    return dst


def py_to_cdr_MapMetaData(src: MapMetaData) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_MapMetaData(writer, src)
    return writer.bytes()


def cdr_to_py_MapMetaData(cdr_payload) -> MapMetaData:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = MapMetaData()
    return cdr_body_to_py_MapMetaData(reader, dst)
