from .pdu_pytype_Image import Image
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_Header import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *



def py_to_cdr_body_Image(writer: CdrWriter, src: Image):
    py_to_cdr_body_Header(writer, src.header)
    writer.write_uint32(src.height)
    writer.write_uint32(src.width)
    writer.write_string(src.encoding)
    writer.write_uint8(src.is_bigendian)
    writer.write_uint32(src.step)
    writer.write_sequence_length(src.data)
    for elem in src.data:
        writer.write_uint8(elem)


def cdr_body_to_py_Image(reader: CdrReader, dst: Image):
    cdr_body_to_py_Header(reader, dst.header)
    dst.height = reader.read_uint32()
    dst.width = reader.read_uint32()
    dst.encoding = reader.read_string()
    dst.is_bigendian = reader.read_uint8()
    dst.step = reader.read_uint32()
    dst.data = [reader.read_uint8() for _ in range(reader.read_uint32())]
    return dst


def py_to_cdr_Image(src: Image) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_Image(writer, src)
    return writer.bytes()


def cdr_to_py_Image(cdr_payload) -> Image:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = Image()
    return cdr_body_to_py_Image(reader, dst)
