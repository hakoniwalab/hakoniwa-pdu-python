from .pdu_pytype_DroneGetStateResponsePacket import DroneGetStateResponsePacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..drone_srv_msgs.pdu_cdr_conv_DroneGetStateResponse import *
from ..hako_msgs.pdu_cdr_conv_HakoBatteryStatus import *
from ..geometry_msgs.pdu_cdr_conv_Point import *
from ..geometry_msgs.pdu_cdr_conv_Pose import *
from ..geometry_msgs.pdu_cdr_conv_Quaternion import *
from ..hako_srv_msgs.pdu_cdr_conv_ServiceResponseHeader import *



def py_to_cdr_body_DroneGetStateResponsePacket(writer: CdrWriter, src: DroneGetStateResponsePacket):
    py_to_cdr_body_ServiceResponseHeader(writer, src.header)
    py_to_cdr_body_DroneGetStateResponse(writer, src.body)


def cdr_body_to_py_DroneGetStateResponsePacket(reader: CdrReader, dst: DroneGetStateResponsePacket):
    cdr_body_to_py_ServiceResponseHeader(reader, dst.header)
    cdr_body_to_py_DroneGetStateResponse(reader, dst.body)
    return dst


def py_to_cdr_DroneGetStateResponsePacket(src: DroneGetStateResponsePacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_DroneGetStateResponsePacket(writer, src)
    return writer.bytes()


def cdr_to_py_DroneGetStateResponsePacket(cdr_payload) -> DroneGetStateResponsePacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = DroneGetStateResponsePacket()
    return cdr_body_to_py_DroneGetStateResponsePacket(reader, dst)
