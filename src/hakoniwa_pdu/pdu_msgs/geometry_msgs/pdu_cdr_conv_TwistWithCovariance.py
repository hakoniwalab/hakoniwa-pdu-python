from .pdu_pytype_TwistWithCovariance import TwistWithCovariance
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..geometry_msgs.pdu_cdr_conv_Twist import *
from ..geometry_msgs.pdu_cdr_conv_Vector3 import *



def py_to_cdr_body_TwistWithCovariance(writer: CdrWriter, src: TwistWithCovariance):
    py_to_cdr_body_Twist(writer, src.twist)
    values = src.covariance
    for i in range(36):
        writer.write_float64(values[i] if i < len(values) else 0.0)


def cdr_body_to_py_TwistWithCovariance(reader: CdrReader, dst: TwistWithCovariance):
    cdr_body_to_py_Twist(reader, dst.twist)
    dst.covariance = [reader.read_float64() for _ in range(36)]
    return dst


def py_to_cdr_TwistWithCovariance(src: TwistWithCovariance) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_TwistWithCovariance(writer, src)
    return writer.bytes()


def cdr_to_py_TwistWithCovariance(cdr_payload) -> TwistWithCovariance:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = TwistWithCovariance()
    return cdr_body_to_py_TwistWithCovariance(reader, dst)
