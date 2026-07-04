from .pdu_pytype_Point32 import Point32
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_Point32(writer: CdrWriter, src: Point32):
    writer.write_float32(src.x)
    writer.write_float32(src.y)
    writer.write_float32(src.z)


def cdr_body_to_py_Point32(reader: CdrReader, dst: Point32):
    dst.x = reader.read_float32()
    dst.y = reader.read_float32()
    dst.z = reader.read_float32()
    return dst


def py_to_cdr_Point32(src: Point32) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_Point32(writer, src)
    return writer.bytes()


def cdr_to_py_Point32(cdr_payload) -> Point32:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = Point32()
    return cdr_body_to_py_Point32(reader, dst)
