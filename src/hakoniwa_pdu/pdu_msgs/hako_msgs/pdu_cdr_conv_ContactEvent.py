from .pdu_pytype_ContactEvent import ContactEvent
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..geometry_msgs.pdu_cdr_conv_Point import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *



def py_to_cdr_body_ContactEvent(writer: CdrWriter, src: ContactEvent):
    py_to_cdr_body_Time(writer, src.stamp)
    writer.write_string(src.self_name)
    writer.write_string(src.other_name)
    writer.write_string(src.other_kind)
    py_to_cdr_body_Point(writer, src.position)
    writer.write_float64(src.relative_speed)
    writer.write_bool(src.started)


def cdr_body_to_py_ContactEvent(reader: CdrReader, dst: ContactEvent):
    cdr_body_to_py_Time(reader, dst.stamp)
    dst.self_name = reader.read_string()
    dst.other_name = reader.read_string()
    dst.other_kind = reader.read_string()
    cdr_body_to_py_Point(reader, dst.position)
    dst.relative_speed = reader.read_float64()
    dst.started = reader.read_bool()
    return dst


def py_to_cdr_ContactEvent(src: ContactEvent) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_ContactEvent(writer, src)
    return writer.bytes()


def cdr_to_py_ContactEvent(cdr_payload) -> ContactEvent:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = ContactEvent()
    return cdr_body_to_py_ContactEvent(reader, dst)
