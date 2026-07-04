from .pdu_pytype_AccelWithCovarianceStamped import AccelWithCovarianceStamped
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..geometry_msgs.pdu_cdr_conv_Accel import *
from ..geometry_msgs.pdu_cdr_conv_AccelWithCovariance import *
from ..std_msgs.pdu_cdr_conv_Header import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *
from ..geometry_msgs.pdu_cdr_conv_Vector3 import *



def py_to_cdr_body_AccelWithCovarianceStamped(writer: CdrWriter, src: AccelWithCovarianceStamped):
    py_to_cdr_body_Header(writer, src.header)
    py_to_cdr_body_AccelWithCovariance(writer, src.accel)


def cdr_body_to_py_AccelWithCovarianceStamped(reader: CdrReader, dst: AccelWithCovarianceStamped):
    cdr_body_to_py_Header(reader, dst.header)
    cdr_body_to_py_AccelWithCovariance(reader, dst.accel)
    return dst


def py_to_cdr_AccelWithCovarianceStamped(src: AccelWithCovarianceStamped) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_AccelWithCovarianceStamped(writer, src)
    return writer.bytes()


def cdr_to_py_AccelWithCovarianceStamped(cdr_payload) -> AccelWithCovarianceStamped:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = AccelWithCovarianceStamped()
    return cdr_body_to_py_AccelWithCovarianceStamped(reader, dst)
