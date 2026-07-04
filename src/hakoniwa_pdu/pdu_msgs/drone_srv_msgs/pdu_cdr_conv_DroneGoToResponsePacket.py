from .pdu_pytype_DroneGoToResponsePacket import DroneGoToResponsePacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..drone_srv_msgs.pdu_cdr_conv_DroneGoToResponse import *
from ..hako_srv_msgs.pdu_cdr_conv_ServiceResponseHeader import *



def py_to_cdr_body_DroneGoToResponsePacket(writer: CdrWriter, src: DroneGoToResponsePacket):
    py_to_cdr_body_ServiceResponseHeader(writer, src.header)
    py_to_cdr_body_DroneGoToResponse(writer, src.body)


def cdr_body_to_py_DroneGoToResponsePacket(reader: CdrReader, dst: DroneGoToResponsePacket):
    cdr_body_to_py_ServiceResponseHeader(reader, dst.header)
    cdr_body_to_py_DroneGoToResponse(reader, dst.body)
    return dst


def py_to_cdr_DroneGoToResponsePacket(src: DroneGoToResponsePacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_DroneGoToResponsePacket(writer, src)
    return writer.bytes()


def cdr_to_py_DroneGoToResponsePacket(cdr_payload) -> DroneGoToResponsePacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = DroneGoToResponsePacket()
    return cdr_body_to_py_DroneGoToResponsePacket(reader, dst)
