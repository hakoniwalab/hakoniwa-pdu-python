from .pdu_pytype_OccupancyGrid import OccupancyGrid
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_Header import *
from ..nav_msgs.pdu_cdr_conv_MapMetaData import *
from ..geometry_msgs.pdu_cdr_conv_Point import *
from ..geometry_msgs.pdu_cdr_conv_Pose import *
from ..geometry_msgs.pdu_cdr_conv_Quaternion import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *



def py_to_cdr_body_OccupancyGrid(writer: CdrWriter, src: OccupancyGrid):
    py_to_cdr_body_Header(writer, src.header)
    py_to_cdr_body_MapMetaData(writer, src.info)
    writer.write_sequence_length(src.data)
    for elem in src.data:
        writer.write_int8(elem)


def cdr_body_to_py_OccupancyGrid(reader: CdrReader, dst: OccupancyGrid):
    cdr_body_to_py_Header(reader, dst.header)
    cdr_body_to_py_MapMetaData(reader, dst.info)
    dst.data = [reader.read_int8() for _ in range(reader.read_uint32())]
    return dst


def py_to_cdr_OccupancyGrid(src: OccupancyGrid) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_OccupancyGrid(writer, src)
    return writer.bytes()


def cdr_to_py_OccupancyGrid(cdr_payload) -> OccupancyGrid:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = OccupancyGrid()
    return cdr_body_to_py_OccupancyGrid(reader, dst)
