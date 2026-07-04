from .pdu_pytype_GridCells import GridCells
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_Header import *
from ..geometry_msgs.pdu_cdr_conv_Point import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *



def py_to_cdr_body_GridCells(writer: CdrWriter, src: GridCells):
    py_to_cdr_body_Header(writer, src.header)
    writer.write_float32(src.cell_width)
    writer.write_float32(src.cell_height)
    writer.write_sequence_length(src.cells)
    for elem in src.cells:
        py_to_cdr_body_Point(writer, elem)


def cdr_body_to_py_GridCells(reader: CdrReader, dst: GridCells):
    cdr_body_to_py_Header(reader, dst.header)
    dst.cell_width = reader.read_float32()
    dst.cell_height = reader.read_float32()
    dst.cells = []
    for _ in range(reader.read_uint32()):
        elem = Point()
        cdr_body_to_py_Point(reader, elem)
        dst.cells.append(elem)
    return dst


def py_to_cdr_GridCells(src: GridCells) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_GridCells(writer, src)
    return writer.bytes()


def cdr_to_py_GridCells(cdr_payload) -> GridCells:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = GridCells()
    return cdr_body_to_py_GridCells(reader, dst)
