from .pdu_pytype_SetLightRequestPacket import SetLightRequestPacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..hako_srv_msgs.pdu_cdr_conv_ServiceRequestHeader import *
from ..hako_srv_msgs.pdu_cdr_conv_SetLightRequest import *



def py_to_cdr_body_SetLightRequestPacket(writer: CdrWriter, src: SetLightRequestPacket):
    py_to_cdr_body_ServiceRequestHeader(writer, src.header)
    py_to_cdr_body_SetLightRequest(writer, src.body)


def cdr_body_to_py_SetLightRequestPacket(reader: CdrReader, dst: SetLightRequestPacket):
    cdr_body_to_py_ServiceRequestHeader(reader, dst.header)
    cdr_body_to_py_SetLightRequest(reader, dst.body)
    return dst


def py_to_cdr_SetLightRequestPacket(src: SetLightRequestPacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_SetLightRequestPacket(writer, src)
    return writer.bytes()


def cdr_to_py_SetLightRequestPacket(cdr_payload) -> SetLightRequestPacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = SetLightRequestPacket()
    return cdr_body_to_py_SetLightRequestPacket(reader, dst)
