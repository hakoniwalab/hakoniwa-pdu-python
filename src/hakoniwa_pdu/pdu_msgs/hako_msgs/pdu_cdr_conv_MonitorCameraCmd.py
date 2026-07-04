from .pdu_pytype_MonitorCameraCmd import MonitorCameraCmd
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..hako_msgs.pdu_cdr_conv_HakoCmdHeader import *



def py_to_cdr_body_MonitorCameraCmd(writer: CdrWriter, src: MonitorCameraCmd):
    py_to_cdr_body_HakoCmdHeader(writer, src.header)
    writer.write_int32(src.request_id)
    writer.write_int32(src.encode_type)
    writer.write_int32(src.request_type)


def cdr_body_to_py_MonitorCameraCmd(reader: CdrReader, dst: MonitorCameraCmd):
    cdr_body_to_py_HakoCmdHeader(reader, dst.header)
    dst.request_id = reader.read_int32()
    dst.encode_type = reader.read_int32()
    dst.request_type = reader.read_int32()
    return dst


def py_to_cdr_MonitorCameraCmd(src: MonitorCameraCmd) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_MonitorCameraCmd(writer, src)
    return writer.bytes()


def cdr_to_py_MonitorCameraCmd(cdr_payload) -> MonitorCameraCmd:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = MonitorCameraCmd()
    return cdr_body_to_py_MonitorCameraCmd(reader, dst)
