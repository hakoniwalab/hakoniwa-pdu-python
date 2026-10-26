from .pdu_pytype_ContactEventArray import ContactEventArray
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..hako_msgs.pdu_cdr_conv_ContactEvent import *
from ..geometry_msgs.pdu_cdr_conv_Point import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *



def py_to_cdr_body_ContactEventArray(writer: CdrWriter, src: ContactEventArray):
    writer.write_sequence_length(src.events)
    for elem in src.events:
        py_to_cdr_body_ContactEvent(writer, elem)


def cdr_body_to_py_ContactEventArray(reader: CdrReader, dst: ContactEventArray):
    dst.events = []
    for _ in range(reader.read_uint32()):
        elem = ContactEvent()
        cdr_body_to_py_ContactEvent(reader, elem)
        dst.events.append(elem)
    return dst


def py_to_cdr_ContactEventArray(src: ContactEventArray) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_ContactEventArray(writer, src)
    return writer.bytes()


def cdr_to_py_ContactEventArray(cdr_payload) -> ContactEventArray:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = ContactEventArray()
    return cdr_body_to_py_ContactEventArray(reader, dst)
