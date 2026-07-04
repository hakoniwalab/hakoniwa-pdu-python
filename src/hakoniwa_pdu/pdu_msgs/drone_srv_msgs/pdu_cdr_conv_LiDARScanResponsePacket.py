from .pdu_pytype_LiDARScanResponsePacket import LiDARScanResponsePacket
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_Header import *
from ..drone_srv_msgs.pdu_cdr_conv_LiDARScanResponse import *
from ..geometry_msgs.pdu_cdr_conv_Point import *
from ..sensor_msgs.pdu_cdr_conv_PointCloud2 import *
from ..sensor_msgs.pdu_cdr_conv_PointField import *
from ..geometry_msgs.pdu_cdr_conv_Pose import *
from ..geometry_msgs.pdu_cdr_conv_Quaternion import *
from ..hako_srv_msgs.pdu_cdr_conv_ServiceResponseHeader import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *



def py_to_cdr_body_LiDARScanResponsePacket(writer: CdrWriter, src: LiDARScanResponsePacket):
    py_to_cdr_body_ServiceResponseHeader(writer, src.header)
    py_to_cdr_body_LiDARScanResponse(writer, src.body)


def cdr_body_to_py_LiDARScanResponsePacket(reader: CdrReader, dst: LiDARScanResponsePacket):
    cdr_body_to_py_ServiceResponseHeader(reader, dst.header)
    cdr_body_to_py_LiDARScanResponse(reader, dst.body)
    return dst


def py_to_cdr_LiDARScanResponsePacket(src: LiDARScanResponsePacket) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_LiDARScanResponsePacket(writer, src)
    return writer.bytes()


def cdr_to_py_LiDARScanResponsePacket(cdr_payload) -> LiDARScanResponsePacket:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = LiDARScanResponsePacket()
    return cdr_body_to_py_LiDARScanResponsePacket(reader, dst)
