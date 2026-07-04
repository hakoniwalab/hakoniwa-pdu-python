from .pdu_pytype_DroneTakeOffResponsePacket import DroneTakeOffResponsePacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..drone_srv_msgs.pdu_cdr_conv_DroneTakeOffResponse import *
from ..hako_srv_msgs.pdu_cdr_conv_ServiceResponseHeader import *



def py_to_cdr_body_DroneTakeOffResponsePacket(writer: CdrWriter, src: DroneTakeOffResponsePacket):
    py_to_cdr_body_ServiceResponseHeader(writer, src.header)
    py_to_cdr_body_DroneTakeOffResponse(writer, src.body)


def cdr_body_to_py_DroneTakeOffResponsePacket(reader: CdrReader, dst: DroneTakeOffResponsePacket):
    cdr_body_to_py_ServiceResponseHeader(reader, dst.header)
    cdr_body_to_py_DroneTakeOffResponse(reader, dst.body)
    return dst


def py_to_cdr_DroneTakeOffResponsePacket(src: DroneTakeOffResponsePacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_DroneTakeOffResponsePacket(writer, src)
    return writer.bytes()


def cdr_to_py_DroneTakeOffResponsePacket(cdr_payload) -> DroneTakeOffResponsePacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = DroneTakeOffResponsePacket()
    return cdr_body_to_py_DroneTakeOffResponsePacket(reader, dst)
