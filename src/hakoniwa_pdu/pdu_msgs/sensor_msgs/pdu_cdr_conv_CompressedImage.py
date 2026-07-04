from .pdu_pytype_CompressedImage import CompressedImage
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_Header import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *



def py_to_cdr_body_CompressedImage(writer: CdrWriter, src: CompressedImage):
    py_to_cdr_body_Header(writer, src.header)
    writer.write_string(src.format)
    writer.write_sequence_length(src.data)
    for elem in src.data:
        writer.write_uint8(elem)


def cdr_body_to_py_CompressedImage(reader: CdrReader, dst: CompressedImage):
    cdr_body_to_py_Header(reader, dst.header)
    dst.format = reader.read_string()
    dst.data = [reader.read_uint8() for _ in range(reader.read_uint32())]
    return dst


def py_to_cdr_CompressedImage(src: CompressedImage) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_CompressedImage(writer, src)
    return writer.bytes()


def cdr_to_py_CompressedImage(cdr_payload) -> CompressedImage:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = CompressedImage()
    return cdr_body_to_py_CompressedImage(reader, dst)
