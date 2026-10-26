from .pdu_pytype_SetLightResponsePacket import SetLightResponsePacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..hako_srv_msgs.pdu_cdr_conv_ServiceResponseHeader import *
from ..hako_srv_msgs.pdu_cdr_conv_SetLightResponse import *



def py_to_cdr_body_SetLightResponsePacket(writer: CdrWriter, src: SetLightResponsePacket):
    py_to_cdr_body_ServiceResponseHeader(writer, src.header)
    py_to_cdr_body_SetLightResponse(writer, src.body)


def cdr_body_to_py_SetLightResponsePacket(reader: CdrReader, dst: SetLightResponsePacket):
    cdr_body_to_py_ServiceResponseHeader(reader, dst.header)
    cdr_body_to_py_SetLightResponse(reader, dst.body)
    return dst


def py_to_cdr_SetLightResponsePacket(src: SetLightResponsePacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_SetLightResponsePacket(writer, src)
    return writer.bytes()


def cdr_to_py_SetLightResponsePacket(cdr_payload) -> SetLightResponsePacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = SetLightResponsePacket()
    return cdr_body_to_py_SetLightResponsePacket(reader, dst)
