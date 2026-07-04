from .pdu_pytype_AddTwoIntsRequestPacket import AddTwoIntsRequestPacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..hako_srv_msgs.pdu_cdr_conv_AddTwoIntsRequest import *
from ..hako_srv_msgs.pdu_cdr_conv_ServiceRequestHeader import *



def py_to_cdr_body_AddTwoIntsRequestPacket(writer: CdrWriter, src: AddTwoIntsRequestPacket):
    py_to_cdr_body_ServiceRequestHeader(writer, src.header)
    py_to_cdr_body_AddTwoIntsRequest(writer, src.body)


def cdr_body_to_py_AddTwoIntsRequestPacket(reader: CdrReader, dst: AddTwoIntsRequestPacket):
    cdr_body_to_py_ServiceRequestHeader(reader, dst.header)
    cdr_body_to_py_AddTwoIntsRequest(reader, dst.body)
    return dst


def py_to_cdr_AddTwoIntsRequestPacket(src: AddTwoIntsRequestPacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_AddTwoIntsRequestPacket(writer, src)
    return writer.bytes()


def cdr_to_py_AddTwoIntsRequestPacket(cdr_payload) -> AddTwoIntsRequestPacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = AddTwoIntsRequestPacket()
    return cdr_body_to_py_AddTwoIntsRequestPacket(reader, dst)
