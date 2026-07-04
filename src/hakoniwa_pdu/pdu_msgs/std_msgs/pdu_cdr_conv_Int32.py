from .pdu_pytype_Int32 import Int32
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_Int32(writer: CdrWriter, src: Int32):
    writer.write_int32(src.data)


def cdr_body_to_py_Int32(reader: CdrReader, dst: Int32):
    dst.data = reader.read_int32()
    return dst


def py_to_cdr_Int32(src: Int32) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_Int32(writer, src)
    return writer.bytes()


def cdr_to_py_Int32(cdr_payload) -> Int32:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = Int32()
    return cdr_body_to_py_Int32(reader, dst)
