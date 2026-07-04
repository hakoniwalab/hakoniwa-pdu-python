from .pdu_pytype_DroneSetReadyResponsePacket import DroneSetReadyResponsePacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..drone_srv_msgs.pdu_cdr_conv_DroneSetReadyResponse import *
from ..hako_srv_msgs.pdu_cdr_conv_ServiceResponseHeader import *



def py_to_cdr_body_DroneSetReadyResponsePacket(writer: CdrWriter, src: DroneSetReadyResponsePacket):
    py_to_cdr_body_ServiceResponseHeader(writer, src.header)
    py_to_cdr_body_DroneSetReadyResponse(writer, src.body)


def cdr_body_to_py_DroneSetReadyResponsePacket(reader: CdrReader, dst: DroneSetReadyResponsePacket):
    cdr_body_to_py_ServiceResponseHeader(reader, dst.header)
    cdr_body_to_py_DroneSetReadyResponse(reader, dst.body)
    return dst


def py_to_cdr_DroneSetReadyResponsePacket(src: DroneSetReadyResponsePacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_DroneSetReadyResponsePacket(writer, src)
    return writer.bytes()


def cdr_to_py_DroneSetReadyResponsePacket(cdr_payload) -> DroneSetReadyResponsePacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = DroneSetReadyResponsePacket()
    return cdr_body_to_py_DroneSetReadyResponsePacket(reader, dst)
