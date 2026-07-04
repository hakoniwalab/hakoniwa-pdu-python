from .pdu_pytype_UInt16 import UInt16
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_UInt16(writer: CdrWriter, src: UInt16):
    writer.write_uint16(src.data)


def cdr_body_to_py_UInt16(reader: CdrReader, dst: UInt16):
    dst.data = reader.read_uint16()
    return dst


def py_to_cdr_UInt16(src: UInt16) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_UInt16(writer, src)
    return writer.bytes()


def cdr_to_py_UInt16(cdr_payload) -> UInt16:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = UInt16()
    return cdr_body_to_py_UInt16(reader, dst)
