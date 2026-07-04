from .pdu_pytype_Quaternion import Quaternion
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_Quaternion(writer: CdrWriter, src: Quaternion):
    writer.write_float64(src.x)
    writer.write_float64(src.y)
    writer.write_float64(src.z)
    writer.write_float64(src.w)


def cdr_body_to_py_Quaternion(reader: CdrReader, dst: Quaternion):
    dst.x = reader.read_float64()
    dst.y = reader.read_float64()
    dst.z = reader.read_float64()
    dst.w = reader.read_float64()
    return dst


def py_to_cdr_Quaternion(src: Quaternion) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_Quaternion(writer, src)
    return writer.bytes()


def cdr_to_py_Quaternion(cdr_payload) -> Quaternion:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = Quaternion()
    return cdr_body_to_py_Quaternion(reader, dst)
