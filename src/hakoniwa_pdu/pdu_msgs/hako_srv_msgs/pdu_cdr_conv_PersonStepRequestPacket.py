from .pdu_pytype_PersonStepRequestPacket import PersonStepRequestPacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..hako_srv_msgs.pdu_cdr_conv_PersonStepRequest import *
from ..hako_srv_msgs.pdu_cdr_conv_ServiceRequestHeader import *
from ..geometry_msgs.pdu_cdr_conv_Twist import *
from ..geometry_msgs.pdu_cdr_conv_Vector3 import *



def py_to_cdr_body_PersonStepRequestPacket(writer: CdrWriter, src: PersonStepRequestPacket):
    py_to_cdr_body_ServiceRequestHeader(writer, src.header)
    py_to_cdr_body_PersonStepRequest(writer, src.body)


def cdr_body_to_py_PersonStepRequestPacket(reader: CdrReader, dst: PersonStepRequestPacket):
    cdr_body_to_py_ServiceRequestHeader(reader, dst.header)
    cdr_body_to_py_PersonStepRequest(reader, dst.body)
    return dst


def py_to_cdr_PersonStepRequestPacket(src: PersonStepRequestPacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_PersonStepRequestPacket(writer, src)
    return writer.bytes()


def cdr_to_py_PersonStepRequestPacket(cdr_payload) -> PersonStepRequestPacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = PersonStepRequestPacket()
    return cdr_body_to_py_PersonStepRequestPacket(reader, dst)
