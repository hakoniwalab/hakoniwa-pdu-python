from .pdu_pytype_DisturbanceBoundary import DisturbanceBoundary
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..geometry_msgs.pdu_cdr_conv_Point import *
from ..geometry_msgs.pdu_cdr_conv_Vector3 import *



def py_to_cdr_body_DisturbanceBoundary(writer: CdrWriter, src: DisturbanceBoundary):
    py_to_cdr_body_Point(writer, src.boundary_point)
    py_to_cdr_body_Vector3(writer, src.boundary_normal)


def cdr_body_to_py_DisturbanceBoundary(reader: CdrReader, dst: DisturbanceBoundary):
    cdr_body_to_py_Point(reader, dst.boundary_point)
    cdr_body_to_py_Vector3(reader, dst.boundary_normal)
    return dst


def py_to_cdr_DisturbanceBoundary(src: DisturbanceBoundary) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_DisturbanceBoundary(writer, src)
    return writer.bytes()


def cdr_to_py_DisturbanceBoundary(cdr_payload) -> DisturbanceBoundary:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = DisturbanceBoundary()
    return cdr_body_to_py_DisturbanceBoundary(reader, dst)
