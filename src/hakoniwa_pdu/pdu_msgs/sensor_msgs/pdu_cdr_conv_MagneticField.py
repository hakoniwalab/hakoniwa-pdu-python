from .pdu_pytype_MagneticField import MagneticField
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_Header import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *
from ..geometry_msgs.pdu_cdr_conv_Vector3 import *



def py_to_cdr_body_MagneticField(writer: CdrWriter, src: MagneticField):
    py_to_cdr_body_Header(writer, src.header)
    py_to_cdr_body_Vector3(writer, src.magnetic_field)
    values = src.magnetic_field_covariance
    for i in range(9):
        writer.write_float64(values[i] if i < len(values) else 0.0)


def cdr_body_to_py_MagneticField(reader: CdrReader, dst: MagneticField):
    cdr_body_to_py_Header(reader, dst.header)
    cdr_body_to_py_Vector3(reader, dst.magnetic_field)
    dst.magnetic_field_covariance = [reader.read_float64() for _ in range(9)]
    return dst


def py_to_cdr_MagneticField(src: MagneticField) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_MagneticField(writer, src)
    return writer.bytes()


def cdr_to_py_MagneticField(cdr_payload) -> MagneticField:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = MagneticField()
    return cdr_body_to_py_MagneticField(reader, dst)
