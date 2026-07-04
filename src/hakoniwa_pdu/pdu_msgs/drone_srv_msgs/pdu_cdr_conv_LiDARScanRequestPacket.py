from .pdu_pytype_LiDARScanRequestPacket import LiDARScanRequestPacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..drone_srv_msgs.pdu_cdr_conv_LiDARScanRequest import *
from ..hako_srv_msgs.pdu_cdr_conv_ServiceRequestHeader import *



def py_to_cdr_body_LiDARScanRequestPacket(writer: CdrWriter, src: LiDARScanRequestPacket):
    py_to_cdr_body_ServiceRequestHeader(writer, src.header)
    py_to_cdr_body_LiDARScanRequest(writer, src.body)


def cdr_body_to_py_LiDARScanRequestPacket(reader: CdrReader, dst: LiDARScanRequestPacket):
    cdr_body_to_py_ServiceRequestHeader(reader, dst.header)
    cdr_body_to_py_LiDARScanRequest(reader, dst.body)
    return dst


def py_to_cdr_LiDARScanRequestPacket(src: LiDARScanRequestPacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_LiDARScanRequestPacket(writer, src)
    return writer.bytes()


def cdr_to_py_LiDARScanRequestPacket(cdr_payload) -> LiDARScanRequestPacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = LiDARScanRequestPacket()
    return cdr_body_to_py_LiDARScanRequestPacket(reader, dst)
