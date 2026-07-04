from .pdu_pytype_Odometry import Odometry
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_Header import *
from ..geometry_msgs.pdu_cdr_conv_Point import *
from ..geometry_msgs.pdu_cdr_conv_Pose import *
from ..geometry_msgs.pdu_cdr_conv_PoseWithCovariance import *
from ..geometry_msgs.pdu_cdr_conv_Quaternion import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *
from ..geometry_msgs.pdu_cdr_conv_Twist import *
from ..geometry_msgs.pdu_cdr_conv_TwistWithCovariance import *
from ..geometry_msgs.pdu_cdr_conv_Vector3 import *



def py_to_cdr_body_Odometry(writer: CdrWriter, src: Odometry):
    py_to_cdr_body_Header(writer, src.header)
    writer.write_string(src.child_frame_id)
    py_to_cdr_body_PoseWithCovariance(writer, src.pose)
    py_to_cdr_body_TwistWithCovariance(writer, src.twist)


def cdr_body_to_py_Odometry(reader: CdrReader, dst: Odometry):
    cdr_body_to_py_Header(reader, dst.header)
    dst.child_frame_id = reader.read_string()
    cdr_body_to_py_PoseWithCovariance(reader, dst.pose)
    cdr_body_to_py_TwistWithCovariance(reader, dst.twist)
    return dst


def py_to_cdr_Odometry(src: Odometry) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_Odometry(writer, src)
    return writer.bytes()


def cdr_to_py_Odometry(cdr_payload) -> Odometry:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = Odometry()
    return cdr_body_to_py_Odometry(reader, dst)
