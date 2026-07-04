from .pdu_pytype_Float64 import Float64
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_Float64(writer: CdrWriter, src: Float64):
    writer.write_float64(src.data)


def cdr_body_to_py_Float64(reader: CdrReader, dst: Float64):
    dst.data = reader.read_float64()
    return dst


def py_to_cdr_Float64(src: Float64) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_Float64(writer, src)
    return writer.bytes()


def cdr_to_py_Float64(cdr_payload) -> Float64:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = Float64()
    return cdr_body_to_py_Float64(reader, dst)
