from .pdu_pytype_DroneSetReadyRequestPacket import DroneSetReadyRequestPacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..drone_srv_msgs.pdu_cdr_conv_DroneSetReadyRequest import *
from ..hako_srv_msgs.pdu_cdr_conv_ServiceRequestHeader import *



def py_to_cdr_body_DroneSetReadyRequestPacket(writer: CdrWriter, src: DroneSetReadyRequestPacket):
    py_to_cdr_body_ServiceRequestHeader(writer, src.header)
    py_to_cdr_body_DroneSetReadyRequest(writer, src.body)


def cdr_body_to_py_DroneSetReadyRequestPacket(reader: CdrReader, dst: DroneSetReadyRequestPacket):
    cdr_body_to_py_ServiceRequestHeader(reader, dst.header)
    cdr_body_to_py_DroneSetReadyRequest(reader, dst.body)
    return dst


def py_to_cdr_DroneSetReadyRequestPacket(src: DroneSetReadyRequestPacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_DroneSetReadyRequestPacket(writer, src)
    return writer.bytes()


def cdr_to_py_DroneSetReadyRequestPacket(cdr_payload) -> DroneSetReadyRequestPacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = DroneSetReadyRequestPacket()
    return cdr_body_to_py_DroneSetReadyRequestPacket(reader, dst)
