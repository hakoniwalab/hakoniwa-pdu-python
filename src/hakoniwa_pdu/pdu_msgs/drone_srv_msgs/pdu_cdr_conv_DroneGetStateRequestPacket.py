from .pdu_pytype_DroneGetStateRequestPacket import DroneGetStateRequestPacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..drone_srv_msgs.pdu_cdr_conv_DroneGetStateRequest import *
from ..hako_srv_msgs.pdu_cdr_conv_ServiceRequestHeader import *



def py_to_cdr_body_DroneGetStateRequestPacket(writer: CdrWriter, src: DroneGetStateRequestPacket):
    py_to_cdr_body_ServiceRequestHeader(writer, src.header)
    py_to_cdr_body_DroneGetStateRequest(writer, src.body)


def cdr_body_to_py_DroneGetStateRequestPacket(reader: CdrReader, dst: DroneGetStateRequestPacket):
    cdr_body_to_py_ServiceRequestHeader(reader, dst.header)
    cdr_body_to_py_DroneGetStateRequest(reader, dst.body)
    return dst


def py_to_cdr_DroneGetStateRequestPacket(src: DroneGetStateRequestPacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_DroneGetStateRequestPacket(writer, src)
    return writer.bytes()


def cdr_to_py_DroneGetStateRequestPacket(cdr_payload) -> DroneGetStateRequestPacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = DroneGetStateRequestPacket()
    return cdr_body_to_py_DroneGetStateRequestPacket(reader, dst)
