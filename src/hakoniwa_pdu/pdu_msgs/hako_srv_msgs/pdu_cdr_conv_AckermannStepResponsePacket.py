from .pdu_pytype_AckermannStepResponsePacket import AckermannStepResponsePacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..hako_srv_msgs.pdu_cdr_conv_AckermannStepResponse import *
from ..geometry_msgs.pdu_cdr_conv_Quaternion import *
from ..hako_srv_msgs.pdu_cdr_conv_ServiceResponseHeader import *
from ..geometry_msgs.pdu_cdr_conv_Transform import *
from ..geometry_msgs.pdu_cdr_conv_Twist import *
from ..geometry_msgs.pdu_cdr_conv_Vector3 import *



def py_to_cdr_body_AckermannStepResponsePacket(writer: CdrWriter, src: AckermannStepResponsePacket):
    py_to_cdr_body_ServiceResponseHeader(writer, src.header)
    py_to_cdr_body_AckermannStepResponse(writer, src.body)


def cdr_body_to_py_AckermannStepResponsePacket(reader: CdrReader, dst: AckermannStepResponsePacket):
    cdr_body_to_py_ServiceResponseHeader(reader, dst.header)
    cdr_body_to_py_AckermannStepResponse(reader, dst.body)
    return dst


def py_to_cdr_AckermannStepResponsePacket(src: AckermannStepResponsePacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_AckermannStepResponsePacket(writer, src)
    return writer.bytes()


def cdr_to_py_AckermannStepResponsePacket(cdr_payload) -> AckermannStepResponsePacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = AckermannStepResponsePacket()
    return cdr_body_to_py_AckermannStepResponsePacket(reader, dst)
