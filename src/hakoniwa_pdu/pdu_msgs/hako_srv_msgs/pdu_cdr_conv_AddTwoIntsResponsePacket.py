from .pdu_pytype_AddTwoIntsResponsePacket import AddTwoIntsResponsePacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..hako_srv_msgs.pdu_cdr_conv_AddTwoIntsResponse import *
from ..hako_srv_msgs.pdu_cdr_conv_ServiceResponseHeader import *



def py_to_cdr_body_AddTwoIntsResponsePacket(writer: CdrWriter, src: AddTwoIntsResponsePacket):
    py_to_cdr_body_ServiceResponseHeader(writer, src.header)
    py_to_cdr_body_AddTwoIntsResponse(writer, src.body)


def cdr_body_to_py_AddTwoIntsResponsePacket(reader: CdrReader, dst: AddTwoIntsResponsePacket):
    cdr_body_to_py_ServiceResponseHeader(reader, dst.header)
    cdr_body_to_py_AddTwoIntsResponse(reader, dst.body)
    return dst


def py_to_cdr_AddTwoIntsResponsePacket(src: AddTwoIntsResponsePacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_AddTwoIntsResponsePacket(writer, src)
    return writer.bytes()


def cdr_to_py_AddTwoIntsResponsePacket(cdr_payload) -> AddTwoIntsResponsePacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = AddTwoIntsResponsePacket()
    return cdr_body_to_py_AddTwoIntsResponsePacket(reader, dst)
