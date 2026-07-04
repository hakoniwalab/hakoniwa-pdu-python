from .pdu_pytype_Range import Range
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_Header import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *



def py_to_cdr_body_Range(writer: CdrWriter, src: Range):
    py_to_cdr_body_Header(writer, src.header)
    writer.write_uint8(src.radiation_type)
    writer.write_float32(src.field_of_view)
    writer.write_float32(src.min_range)
    writer.write_float32(src.max_range)
    writer.write_float32(src.range)
    writer.write_float32(src.variance)


def cdr_body_to_py_Range(reader: CdrReader, dst: Range):
    cdr_body_to_py_Header(reader, dst.header)
    dst.radiation_type = reader.read_uint8()
    dst.field_of_view = reader.read_float32()
    dst.min_range = reader.read_float32()
    dst.max_range = reader.read_float32()
    dst.range = reader.read_float32()
    dst.variance = reader.read_float32()
    return dst


def py_to_cdr_Range(src: Range) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_Range(writer, src)
    return writer.bytes()


def cdr_to_py_Range(cdr_payload) -> Range:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = Range()
    return cdr_body_to_py_Range(reader, dst)
