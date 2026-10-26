from .pdu_pytype_PersonStepResponsePacket import PersonStepResponsePacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_Header import *
from ..sensor_msgs.pdu_cdr_conv_JointState import *
from ..hako_srv_msgs.pdu_cdr_conv_PersonStepResponse import *
from ..geometry_msgs.pdu_cdr_conv_Quaternion import *
from ..hako_srv_msgs.pdu_cdr_conv_ServiceResponseHeader import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *
from ..geometry_msgs.pdu_cdr_conv_Transform import *
from ..geometry_msgs.pdu_cdr_conv_Twist import *
from ..geometry_msgs.pdu_cdr_conv_Vector3 import *



def py_to_cdr_body_PersonStepResponsePacket(writer: CdrWriter, src: PersonStepResponsePacket):
    py_to_cdr_body_ServiceResponseHeader(writer, src.header)
    py_to_cdr_body_PersonStepResponse(writer, src.body)


def cdr_body_to_py_PersonStepResponsePacket(reader: CdrReader, dst: PersonStepResponsePacket):
    cdr_body_to_py_ServiceResponseHeader(reader, dst.header)
    cdr_body_to_py_PersonStepResponse(reader, dst.body)
    return dst


def py_to_cdr_PersonStepResponsePacket(src: PersonStepResponsePacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_PersonStepResponsePacket(writer, src)
    return writer.bytes()


def cdr_to_py_PersonStepResponsePacket(cdr_payload) -> PersonStepResponsePacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = PersonStepResponsePacket()
    return cdr_body_to_py_PersonStepResponsePacket(reader, dst)
