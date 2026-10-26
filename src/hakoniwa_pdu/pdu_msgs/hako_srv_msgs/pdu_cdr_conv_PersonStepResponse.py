from .pdu_pytype_PersonStepResponse import PersonStepResponse
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_Header import *
from ..sensor_msgs.pdu_cdr_conv_JointState import *
from ..geometry_msgs.pdu_cdr_conv_Quaternion import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *
from ..geometry_msgs.pdu_cdr_conv_Transform import *
from ..geometry_msgs.pdu_cdr_conv_Twist import *
from ..geometry_msgs.pdu_cdr_conv_Vector3 import *



def py_to_cdr_body_PersonStepResponse(writer: CdrWriter, src: PersonStepResponse):
    writer.write_uint64(src.step)
    writer.write_uint32(src.result_code)
    writer.write_uint64(src.sim_time_usec)
    py_to_cdr_body_Transform(writer, src.pose)
    py_to_cdr_body_Twist(writer, src.twist)
    py_to_cdr_body_JointState(writer, src.joints)


def cdr_body_to_py_PersonStepResponse(reader: CdrReader, dst: PersonStepResponse):
    dst.step = reader.read_uint64()
    dst.result_code = reader.read_uint32()
    dst.sim_time_usec = reader.read_uint64()
    cdr_body_to_py_Transform(reader, dst.pose)
    cdr_body_to_py_Twist(reader, dst.twist)
    cdr_body_to_py_JointState(reader, dst.joints)
    return dst


def py_to_cdr_PersonStepResponse(src: PersonStepResponse) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_PersonStepResponse(writer, src)
    return writer.bytes()


def cdr_to_py_PersonStepResponse(cdr_payload) -> PersonStepResponse:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = PersonStepResponse()
    return cdr_body_to_py_PersonStepResponse(reader, dst)
