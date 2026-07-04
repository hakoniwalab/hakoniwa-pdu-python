from .pdu_pytype_UInt32 import UInt32
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_UInt32(writer: CdrWriter, src: UInt32):
    writer.write_uint32(src.data)


def cdr_body_to_py_UInt32(reader: CdrReader, dst: UInt32):
    dst.data = reader.read_uint32()
    return dst


def py_to_cdr_UInt32(src: UInt32) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_UInt32(writer, src)
    return writer.bytes()


def cdr_to_py_UInt32(cdr_payload) -> UInt32:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = UInt32()
    return cdr_body_to_py_UInt32(reader, dst)
