from .pdu_pytype_Vector3 import Vector3
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_Vector3(writer: CdrWriter, src: Vector3):
    writer.write_float64(src.x)
    writer.write_float64(src.y)
    writer.write_float64(src.z)


def cdr_body_to_py_Vector3(reader: CdrReader, dst: Vector3):
    dst.x = reader.read_float64()
    dst.y = reader.read_float64()
    dst.z = reader.read_float64()
    return dst


def py_to_cdr_Vector3(src: Vector3) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_Vector3(writer, src)
    return writer.bytes()


def cdr_to_py_Vector3(cdr_payload) -> Vector3:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = Vector3()
    return cdr_body_to_py_Vector3(reader, dst)
