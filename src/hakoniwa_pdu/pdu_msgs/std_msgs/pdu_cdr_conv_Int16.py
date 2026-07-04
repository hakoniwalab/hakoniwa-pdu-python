from .pdu_pytype_Int16 import Int16
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_Int16(writer: CdrWriter, src: Int16):
    writer.write_int16(src.data)


def cdr_body_to_py_Int16(reader: CdrReader, dst: Int16):
    dst.data = reader.read_int16()
    return dst


def py_to_cdr_Int16(src: Int16) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_Int16(writer, src)
    return writer.bytes()


def cdr_to_py_Int16(cdr_payload) -> Int16:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = Int16()
    return cdr_body_to_py_Int16(reader, dst)
