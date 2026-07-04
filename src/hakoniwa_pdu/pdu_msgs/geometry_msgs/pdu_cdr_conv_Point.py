from .pdu_pytype_Point import Point
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_Point(writer: CdrWriter, src: Point):
    writer.write_float64(src.x)
    writer.write_float64(src.y)
    writer.write_float64(src.z)


def cdr_body_to_py_Point(reader: CdrReader, dst: Point):
    dst.x = reader.read_float64()
    dst.y = reader.read_float64()
    dst.z = reader.read_float64()
    return dst


def py_to_cdr_Point(src: Point) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_Point(writer, src)
    return writer.bytes()


def cdr_to_py_Point(cdr_payload) -> Point:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = Point()
    return cdr_body_to_py_Point(reader, dst)
