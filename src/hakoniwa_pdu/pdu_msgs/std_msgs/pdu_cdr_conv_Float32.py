from .pdu_pytype_Float32 import Float32
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_Float32(writer: CdrWriter, src: Float32):
    writer.write_float32(src.data)


def cdr_body_to_py_Float32(reader: CdrReader, dst: Float32):
    dst.data = reader.read_float32()
    return dst


def py_to_cdr_Float32(src: Float32) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_Float32(writer, src)
    return writer.bytes()


def cdr_to_py_Float32(cdr_payload) -> Float32:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = Float32()
    return cdr_body_to_py_Float32(reader, dst)
