from .pdu_pytype_Int64 import Int64
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_Int64(writer: CdrWriter, src: Int64):
    writer.write_int64(src.data)


def cdr_body_to_py_Int64(reader: CdrReader, dst: Int64):
    dst.data = reader.read_int64()
    return dst


def py_to_cdr_Int64(src: Int64) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_Int64(writer, src)
    return writer.bytes()


def cdr_to_py_Int64(cdr_payload) -> Int64:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = Int64()
    return cdr_body_to_py_Int64(reader, dst)
