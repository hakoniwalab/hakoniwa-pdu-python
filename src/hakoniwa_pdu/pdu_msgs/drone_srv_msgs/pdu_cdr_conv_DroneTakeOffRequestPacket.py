from .pdu_pytype_DroneTakeOffRequestPacket import DroneTakeOffRequestPacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..drone_srv_msgs.pdu_cdr_conv_DroneTakeOffRequest import *
from ..hako_srv_msgs.pdu_cdr_conv_ServiceRequestHeader import *



def py_to_cdr_body_DroneTakeOffRequestPacket(writer: CdrWriter, src: DroneTakeOffRequestPacket):
    py_to_cdr_body_ServiceRequestHeader(writer, src.header)
    py_to_cdr_body_DroneTakeOffRequest(writer, src.body)


def cdr_body_to_py_DroneTakeOffRequestPacket(reader: CdrReader, dst: DroneTakeOffRequestPacket):
    cdr_body_to_py_ServiceRequestHeader(reader, dst.header)
    cdr_body_to_py_DroneTakeOffRequest(reader, dst.body)
    return dst


def py_to_cdr_DroneTakeOffRequestPacket(src: DroneTakeOffRequestPacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_DroneTakeOffRequestPacket(writer, src)
    return writer.bytes()


def cdr_to_py_DroneTakeOffRequestPacket(cdr_payload) -> DroneTakeOffRequestPacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = DroneTakeOffRequestPacket()
    return cdr_body_to_py_DroneTakeOffRequestPacket(reader, dst)
