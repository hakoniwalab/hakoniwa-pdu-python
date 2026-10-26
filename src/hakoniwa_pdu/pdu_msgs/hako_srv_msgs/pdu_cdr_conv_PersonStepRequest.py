from .pdu_pytype_PersonStepRequest import PersonStepRequest
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..geometry_msgs.pdu_cdr_conv_Twist import *
from ..geometry_msgs.pdu_cdr_conv_Vector3 import *



def py_to_cdr_body_PersonStepRequest(writer: CdrWriter, src: PersonStepRequest):
    writer.write_uint64(src.step)
    py_to_cdr_body_Twist(writer, src.cmd_vel)
    writer.write_string(src.animation)
    writer.write_string(src.ride)


def cdr_body_to_py_PersonStepRequest(reader: CdrReader, dst: PersonStepRequest):
    dst.step = reader.read_uint64()
    cdr_body_to_py_Twist(reader, dst.cmd_vel)
    dst.animation = reader.read_string()
    dst.ride = reader.read_string()
    return dst


def py_to_cdr_PersonStepRequest(src: PersonStepRequest) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_PersonStepRequest(writer, src)
    return writer.bytes()


def cdr_to_py_PersonStepRequest(cdr_payload) -> PersonStepRequest:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = PersonStepRequest()
    return cdr_body_to_py_PersonStepRequest(reader, dst)
