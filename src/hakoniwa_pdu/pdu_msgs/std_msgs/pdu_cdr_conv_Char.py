from .pdu_pytype_Char import Char
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_Char(writer: CdrWriter, src: Char):
    writer.write_uint8(src.data)


def cdr_body_to_py_Char(reader: CdrReader, dst: Char):
    dst.data = reader.read_uint8()
    return dst


def py_to_cdr_Char(src: Char) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_Char(writer, src)
    return writer.bytes()


def cdr_to_py_Char(cdr_payload) -> Char:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = Char()
    return cdr_body_to_py_Char(reader, dst)
