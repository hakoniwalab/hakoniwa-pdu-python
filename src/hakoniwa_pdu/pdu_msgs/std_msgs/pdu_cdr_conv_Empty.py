from .pdu_pytype_Empty import Empty
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_Empty(writer: CdrWriter, src: Empty):
    writer.write_uint8(src.hako_dummy)


def cdr_body_to_py_Empty(reader: CdrReader, dst: Empty):
    dst.hako_dummy = reader.read_uint8()
    return dst


def py_to_cdr_Empty(src: Empty) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_Empty(writer, src)
    return writer.bytes()


def cdr_to_py_Empty(cdr_payload) -> Empty:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = Empty()
    return cdr_body_to_py_Empty(reader, dst)
