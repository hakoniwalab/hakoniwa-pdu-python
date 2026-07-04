from .pdu_pytype_Header import Header
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..builtin_interfaces.pdu_cdr_conv_Time import *



def py_to_cdr_body_Header(writer: CdrWriter, src: Header):
    py_to_cdr_body_Time(writer, src.stamp)
    writer.write_string(src.frame_id)


def cdr_body_to_py_Header(reader: CdrReader, dst: Header):
    cdr_body_to_py_Time(reader, dst.stamp)
    dst.frame_id = reader.read_string()
    return dst


def py_to_cdr_Header(src: Header) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_Header(writer, src)
    return writer.bytes()


def cdr_to_py_Header(cdr_payload) -> Header:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = Header()
    return cdr_body_to_py_Header(reader, dst)
