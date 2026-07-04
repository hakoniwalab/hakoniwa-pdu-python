from .pdu_pytype_Int8 import Int8
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_Int8(writer: CdrWriter, src: Int8):
    writer.write_int8(src.data)


def cdr_body_to_py_Int8(reader: CdrReader, dst: Int8):
    dst.data = reader.read_int8()
    return dst


def py_to_cdr_Int8(src: Int8) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_Int8(writer, src)
    return writer.bytes()


def cdr_to_py_Int8(cdr_payload) -> Int8:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = Int8()
    return cdr_body_to_py_Int8(reader, dst)
