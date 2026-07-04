from .pdu_pytype_UInt64 import UInt64
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_UInt64(writer: CdrWriter, src: UInt64):
    writer.write_uint64(src.data)


def cdr_body_to_py_UInt64(reader: CdrReader, dst: UInt64):
    dst.data = reader.read_uint64()
    return dst


def py_to_cdr_UInt64(src: UInt64) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_UInt64(writer, src)
    return writer.bytes()


def cdr_to_py_UInt64(cdr_payload) -> UInt64:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = UInt64()
    return cdr_body_to_py_UInt64(reader, dst)
