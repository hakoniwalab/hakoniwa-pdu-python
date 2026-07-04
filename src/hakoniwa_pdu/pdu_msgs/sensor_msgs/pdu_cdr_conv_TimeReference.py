from .pdu_pytype_TimeReference import TimeReference
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_Header import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *



def py_to_cdr_body_TimeReference(writer: CdrWriter, src: TimeReference):
    py_to_cdr_body_Header(writer, src.header)
    py_to_cdr_body_Time(writer, src.time_ref)
    writer.write_string(src.source)


def cdr_body_to_py_TimeReference(reader: CdrReader, dst: TimeReference):
    cdr_body_to_py_Header(reader, dst.header)
    cdr_body_to_py_Time(reader, dst.time_ref)
    dst.source = reader.read_string()
    return dst


def py_to_cdr_TimeReference(src: TimeReference) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_TimeReference(writer, src)
    return writer.bytes()


def cdr_to_py_TimeReference(cdr_payload) -> TimeReference:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = TimeReference()
    return cdr_body_to_py_TimeReference(reader, dst)
