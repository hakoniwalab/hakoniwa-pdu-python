from .pdu_pytype_DroneLandResponsePacket import DroneLandResponsePacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..drone_srv_msgs.pdu_cdr_conv_DroneLandResponse import *
from ..hako_srv_msgs.pdu_cdr_conv_ServiceResponseHeader import *



def py_to_cdr_body_DroneLandResponsePacket(writer: CdrWriter, src: DroneLandResponsePacket):
    py_to_cdr_body_ServiceResponseHeader(writer, src.header)
    py_to_cdr_body_DroneLandResponse(writer, src.body)


def cdr_body_to_py_DroneLandResponsePacket(reader: CdrReader, dst: DroneLandResponsePacket):
    cdr_body_to_py_ServiceResponseHeader(reader, dst.header)
    cdr_body_to_py_DroneLandResponse(reader, dst.body)
    return dst


def py_to_cdr_DroneLandResponsePacket(src: DroneLandResponsePacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_DroneLandResponsePacket(writer, src)
    return writer.bytes()


def cdr_to_py_DroneLandResponsePacket(cdr_payload) -> DroneLandResponsePacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = DroneLandResponsePacket()
    return cdr_body_to_py_DroneLandResponsePacket(reader, dst)
