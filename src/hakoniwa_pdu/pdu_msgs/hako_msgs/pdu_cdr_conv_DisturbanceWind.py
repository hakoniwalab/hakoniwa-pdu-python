from .pdu_pytype_DisturbanceWind import DisturbanceWind
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..geometry_msgs.pdu_cdr_conv_Vector3 import *



def py_to_cdr_body_DisturbanceWind(writer: CdrWriter, src: DisturbanceWind):
    py_to_cdr_body_Vector3(writer, src.value)


def cdr_body_to_py_DisturbanceWind(reader: CdrReader, dst: DisturbanceWind):
    cdr_body_to_py_Vector3(reader, dst.value)
    return dst


def py_to_cdr_DisturbanceWind(src: DisturbanceWind) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_DisturbanceWind(writer, src)
    return writer.bytes()


def cdr_to_py_DisturbanceWind(cdr_payload) -> DisturbanceWind:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = DisturbanceWind()
    return cdr_body_to_py_DisturbanceWind(reader, dst)
