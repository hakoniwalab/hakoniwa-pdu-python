from .pdu_pytype_MonitorCameraData import MonitorCameraData
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..sensor_msgs.pdu_cdr_conv_CompressedImage import *
from ..std_msgs.pdu_cdr_conv_Header import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *



def py_to_cdr_body_MonitorCameraData(writer: CdrWriter, src: MonitorCameraData):
    writer.write_int32(src.request_id)
    writer.write_int32(src.image_data_length)
    py_to_cdr_body_CompressedImage(writer, src.image)


def cdr_body_to_py_MonitorCameraData(reader: CdrReader, dst: MonitorCameraData):
    dst.request_id = reader.read_int32()
    dst.image_data_length = reader.read_int32()
    cdr_body_to_py_CompressedImage(reader, dst.image)
    return dst


def py_to_cdr_MonitorCameraData(src: MonitorCameraData) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_MonitorCameraData(writer, src)
    return writer.bytes()


def cdr_to_py_MonitorCameraData(cdr_payload) -> MonitorCameraData:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = MonitorCameraData()
    return cdr_body_to_py_MonitorCameraData(reader, dst)
