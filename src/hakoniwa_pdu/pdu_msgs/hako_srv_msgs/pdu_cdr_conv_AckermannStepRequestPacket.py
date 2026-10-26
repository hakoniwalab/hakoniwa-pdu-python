from .pdu_pytype_AckermannStepRequestPacket import AckermannStepRequestPacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..ackermann_msgs.pdu_cdr_conv_AckermannDrive import *
from ..hako_srv_msgs.pdu_cdr_conv_AckermannStepRequest import *
from ..hako_srv_msgs.pdu_cdr_conv_ServiceRequestHeader import *



def py_to_cdr_body_AckermannStepRequestPacket(writer: CdrWriter, src: AckermannStepRequestPacket):
    py_to_cdr_body_ServiceRequestHeader(writer, src.header)
    py_to_cdr_body_AckermannStepRequest(writer, src.body)


def cdr_body_to_py_AckermannStepRequestPacket(reader: CdrReader, dst: AckermannStepRequestPacket):
    cdr_body_to_py_ServiceRequestHeader(reader, dst.header)
    cdr_body_to_py_AckermannStepRequest(reader, dst.body)
    return dst


def py_to_cdr_AckermannStepRequestPacket(src: AckermannStepRequestPacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_AckermannStepRequestPacket(writer, src)
    return writer.bytes()


def cdr_to_py_AckermannStepRequestPacket(cdr_payload) -> AckermannStepRequestPacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = AckermannStepRequestPacket()
    return cdr_body_to_py_AckermannStepRequestPacket(reader, dst)
