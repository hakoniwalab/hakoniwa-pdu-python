from .pdu_pytype_PoseWithCovarianceStamped import PoseWithCovarianceStamped
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_Header import *
from ..geometry_msgs.pdu_cdr_conv_Point import *
from ..geometry_msgs.pdu_cdr_conv_Pose import *
from ..geometry_msgs.pdu_cdr_conv_PoseWithCovariance import *
from ..geometry_msgs.pdu_cdr_conv_Quaternion import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *



def py_to_cdr_body_PoseWithCovarianceStamped(writer: CdrWriter, src: PoseWithCovarianceStamped):
    py_to_cdr_body_Header(writer, src.header)
    py_to_cdr_body_PoseWithCovariance(writer, src.pose)


def cdr_body_to_py_PoseWithCovarianceStamped(reader: CdrReader, dst: PoseWithCovarianceStamped):
    cdr_body_to_py_Header(reader, dst.header)
    cdr_body_to_py_PoseWithCovariance(reader, dst.pose)
    return dst


def py_to_cdr_PoseWithCovarianceStamped(src: PoseWithCovarianceStamped) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_PoseWithCovarianceStamped(writer, src)
    return writer.bytes()


def cdr_to_py_PoseWithCovarianceStamped(cdr_payload) -> PoseWithCovarianceStamped:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = PoseWithCovarianceStamped()
    return cdr_body_to_py_PoseWithCovarianceStamped(reader, dst)
