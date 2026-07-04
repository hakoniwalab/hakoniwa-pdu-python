from .pdu_pytype_DroneLandRequestPacket import DroneLandRequestPacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..drone_srv_msgs.pdu_cdr_conv_DroneLandRequest import *
from ..hako_srv_msgs.pdu_cdr_conv_ServiceRequestHeader import *



def py_to_cdr_body_DroneLandRequestPacket(writer: CdrWriter, src: DroneLandRequestPacket):
    py_to_cdr_body_ServiceRequestHeader(writer, src.header)
    py_to_cdr_body_DroneLandRequest(writer, src.body)


def cdr_body_to_py_DroneLandRequestPacket(reader: CdrReader, dst: DroneLandRequestPacket):
    cdr_body_to_py_ServiceRequestHeader(reader, dst.header)
    cdr_body_to_py_DroneLandRequest(reader, dst.body)
    return dst


def py_to_cdr_DroneLandRequestPacket(src: DroneLandRequestPacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_DroneLandRequestPacket(writer, src)
    return writer.bytes()


def cdr_to_py_DroneLandRequestPacket(cdr_payload) -> DroneLandRequestPacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = DroneLandRequestPacket()
    return cdr_body_to_py_DroneLandRequestPacket(reader, dst)
