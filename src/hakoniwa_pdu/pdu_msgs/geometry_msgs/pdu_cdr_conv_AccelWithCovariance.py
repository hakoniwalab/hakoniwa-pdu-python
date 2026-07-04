from .pdu_pytype_AccelWithCovariance import AccelWithCovariance
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..geometry_msgs.pdu_cdr_conv_Accel import *
from ..geometry_msgs.pdu_cdr_conv_Vector3 import *



def py_to_cdr_body_AccelWithCovariance(writer: CdrWriter, src: AccelWithCovariance):
    py_to_cdr_body_Accel(writer, src.accel)
    values = src.covariance
    for i in range(36):
        writer.write_float64(values[i] if i < len(values) else 0.0)


def cdr_body_to_py_AccelWithCovariance(reader: CdrReader, dst: AccelWithCovariance):
    cdr_body_to_py_Accel(reader, dst.accel)
    dst.covariance = [reader.read_float64() for _ in range(36)]
    return dst


def py_to_cdr_AccelWithCovariance(src: AccelWithCovariance) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_AccelWithCovariance(writer, src)
    return writer.bytes()


def cdr_to_py_AccelWithCovariance(cdr_payload) -> AccelWithCovariance:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = AccelWithCovariance()
    return cdr_body_to_py_AccelWithCovariance(reader, dst)
