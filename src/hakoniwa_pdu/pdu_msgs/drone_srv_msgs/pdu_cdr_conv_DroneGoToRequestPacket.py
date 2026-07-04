from .pdu_pytype_DroneGoToRequestPacket import DroneGoToRequestPacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..drone_srv_msgs.pdu_cdr_conv_DroneGoToRequest import *
from ..hako_srv_msgs.pdu_cdr_conv_ServiceRequestHeader import *
from ..geometry_msgs.pdu_cdr_conv_Vector3 import *



def py_to_cdr_body_DroneGoToRequestPacket(writer: CdrWriter, src: DroneGoToRequestPacket):
    py_to_cdr_body_ServiceRequestHeader(writer, src.header)
    py_to_cdr_body_DroneGoToRequest(writer, src.body)


def cdr_body_to_py_DroneGoToRequestPacket(reader: CdrReader, dst: DroneGoToRequestPacket):
    cdr_body_to_py_ServiceRequestHeader(reader, dst.header)
    cdr_body_to_py_DroneGoToRequest(reader, dst.body)
    return dst


def py_to_cdr_DroneGoToRequestPacket(src: DroneGoToRequestPacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_DroneGoToRequestPacket(writer, src)
    return writer.bytes()


def cdr_to_py_DroneGoToRequestPacket(cdr_payload) -> DroneGoToRequestPacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = DroneGoToRequestPacket()
    return cdr_body_to_py_DroneGoToRequestPacket(reader, dst)
