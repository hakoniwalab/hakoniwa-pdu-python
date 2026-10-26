from .pdu_pytype_AckermannStepResponse import AckermannStepResponse
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..geometry_msgs.pdu_cdr_conv_Quaternion import *
from ..geometry_msgs.pdu_cdr_conv_Transform import *
from ..geometry_msgs.pdu_cdr_conv_Twist import *
from ..geometry_msgs.pdu_cdr_conv_Vector3 import *



def py_to_cdr_body_AckermannStepResponse(writer: CdrWriter, src: AckermannStepResponse):
    writer.write_uint64(src.step)
    writer.write_uint32(src.result_code)
    writer.write_uint64(src.sim_time_usec)
    py_to_cdr_body_Transform(writer, src.pose)
    py_to_cdr_body_Twist(writer, src.twist)


def cdr_body_to_py_AckermannStepResponse(reader: CdrReader, dst: AckermannStepResponse):
    dst.step = reader.read_uint64()
    dst.result_code = reader.read_uint32()
    dst.sim_time_usec = reader.read_uint64()
    cdr_body_to_py_Transform(reader, dst.pose)
    cdr_body_to_py_Twist(reader, dst.twist)
    return dst


def py_to_cdr_AckermannStepResponse(src: AckermannStepResponse) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_AckermannStepResponse(writer, src)
    return writer.bytes()


def cdr_to_py_AckermannStepResponse(cdr_payload) -> AckermannStepResponse:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = AckermannStepResponse()
    return cdr_body_to_py_AckermannStepResponse(reader, dst)
