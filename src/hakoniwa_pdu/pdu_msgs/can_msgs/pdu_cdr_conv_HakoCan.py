from .pdu_pytype_HakoCan import HakoCan
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..can_msgs.pdu_cdr_conv_HakoCanBody import *
from ..can_msgs.pdu_cdr_conv_HakoCanHead import *



def py_to_cdr_body_HakoCan(writer: CdrWriter, src: HakoCan):
    py_to_cdr_body_HakoCanHead(writer, src.head)
    py_to_cdr_body_HakoCanBody(writer, src.body)


def cdr_body_to_py_HakoCan(reader: CdrReader, dst: HakoCan):
    cdr_body_to_py_HakoCanHead(reader, dst.head)
    cdr_body_to_py_HakoCanBody(reader, dst.body)
    return dst


def py_to_cdr_HakoCan(src: HakoCan) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_HakoCan(writer, src)
    return writer.bytes()


def cdr_to_py_HakoCan(cdr_payload) -> HakoCan:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = HakoCan()
    return cdr_body_to_py_HakoCan(reader, dst)
