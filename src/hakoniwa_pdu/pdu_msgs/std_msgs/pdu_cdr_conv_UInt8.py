from .pdu_pytype_UInt8 import UInt8
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_UInt8(writer: CdrWriter, src: UInt8):
    writer.write_uint8(src.data)


def cdr_body_to_py_UInt8(reader: CdrReader, dst: UInt8):
    dst.data = reader.read_uint8()
    return dst


def py_to_cdr_UInt8(src: UInt8) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_UInt8(writer, src)
    return writer.bytes()


def cdr_to_py_UInt8(cdr_payload) -> UInt8:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = UInt8()
    return cdr_body_to_py_UInt8(reader, dst)
