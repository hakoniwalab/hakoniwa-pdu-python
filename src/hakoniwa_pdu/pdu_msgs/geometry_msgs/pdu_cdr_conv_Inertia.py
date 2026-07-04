from .pdu_pytype_Inertia import Inertia
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..geometry_msgs.pdu_cdr_conv_Vector3 import *



def py_to_cdr_body_Inertia(writer: CdrWriter, src: Inertia):
    writer.write_float64(src.m)
    py_to_cdr_body_Vector3(writer, src.com)
    writer.write_float64(src.ixx)
    writer.write_float64(src.ixy)
    writer.write_float64(src.ixz)
    writer.write_float64(src.iyy)
    writer.write_float64(src.iyz)
    writer.write_float64(src.izz)


def cdr_body_to_py_Inertia(reader: CdrReader, dst: Inertia):
    dst.m = reader.read_float64()
    cdr_body_to_py_Vector3(reader, dst.com)
    dst.ixx = reader.read_float64()
    dst.ixy = reader.read_float64()
    dst.ixz = reader.read_float64()
    dst.iyy = reader.read_float64()
    dst.iyz = reader.read_float64()
    dst.izz = reader.read_float64()
    return dst


def py_to_cdr_Inertia(src: Inertia) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_Inertia(writer, src)
    return writer.bytes()


def cdr_to_py_Inertia(cdr_payload) -> Inertia:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = Inertia()
    return cdr_body_to_py_Inertia(reader, dst)
