from .pdu_pytype_TwistWithCovarianceStamped import TwistWithCovarianceStamped
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_Header import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *
from ..geometry_msgs.pdu_cdr_conv_Twist import *
from ..geometry_msgs.pdu_cdr_conv_TwistWithCovariance import *
from ..geometry_msgs.pdu_cdr_conv_Vector3 import *



def py_to_cdr_body_TwistWithCovarianceStamped(writer: CdrWriter, src: TwistWithCovarianceStamped):
    py_to_cdr_body_Header(writer, src.header)
    py_to_cdr_body_TwistWithCovariance(writer, src.twist)


def cdr_body_to_py_TwistWithCovarianceStamped(reader: CdrReader, dst: TwistWithCovarianceStamped):
    cdr_body_to_py_Header(reader, dst.header)
    cdr_body_to_py_TwistWithCovariance(reader, dst.twist)
    return dst


def py_to_cdr_TwistWithCovarianceStamped(src: TwistWithCovarianceStamped) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_TwistWithCovarianceStamped(writer, src)
    return writer.bytes()


def cdr_to_py_TwistWithCovarianceStamped(cdr_payload) -> TwistWithCovarianceStamped:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = TwistWithCovarianceStamped()
    return cdr_body_to_py_TwistWithCovarianceStamped(reader, dst)
