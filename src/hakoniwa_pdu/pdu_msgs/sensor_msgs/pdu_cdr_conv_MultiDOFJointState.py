from .pdu_pytype_MultiDOFJointState import MultiDOFJointState
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_Header import *
from ..geometry_msgs.pdu_cdr_conv_Quaternion import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *
from ..geometry_msgs.pdu_cdr_conv_Transform import *
from ..geometry_msgs.pdu_cdr_conv_Twist import *
from ..geometry_msgs.pdu_cdr_conv_Vector3 import *
from ..geometry_msgs.pdu_cdr_conv_Wrench import *



def py_to_cdr_body_MultiDOFJointState(writer: CdrWriter, src: MultiDOFJointState):
    py_to_cdr_body_Header(writer, src.header)
    writer.write_sequence_length(src.joint_names)
    for elem in src.joint_names:
        writer.write_string(elem)
    writer.write_sequence_length(src.transforms)
    for elem in src.transforms:
        py_to_cdr_body_Transform(writer, elem)
    writer.write_sequence_length(src.twist)
    for elem in src.twist:
        py_to_cdr_body_Twist(writer, elem)
    writer.write_sequence_length(src.wrench)
    for elem in src.wrench:
        py_to_cdr_body_Wrench(writer, elem)


def cdr_body_to_py_MultiDOFJointState(reader: CdrReader, dst: MultiDOFJointState):
    cdr_body_to_py_Header(reader, dst.header)
    dst.joint_names = [reader.read_string() for _ in range(reader.read_uint32())]
    dst.transforms = []
    for _ in range(reader.read_uint32()):
        elem = Transform()
        cdr_body_to_py_Transform(reader, elem)
        dst.transforms.append(elem)
    dst.twist = []
    for _ in range(reader.read_uint32()):
        elem = Twist()
        cdr_body_to_py_Twist(reader, elem)
        dst.twist.append(elem)
    dst.wrench = []
    for _ in range(reader.read_uint32()):
        elem = Wrench()
        cdr_body_to_py_Wrench(reader, elem)
        dst.wrench.append(elem)
    return dst


def py_to_cdr_MultiDOFJointState(src: MultiDOFJointState) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_MultiDOFJointState(writer, src)
    return writer.bytes()


def cdr_to_py_MultiDOFJointState(cdr_payload) -> MultiDOFJointState:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = MultiDOFJointState()
    return cdr_body_to_py_MultiDOFJointState(reader, dst)
