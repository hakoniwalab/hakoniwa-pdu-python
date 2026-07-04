from .pdu_pytype_DroneGetStateResponse import DroneGetStateResponse
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..hako_msgs.pdu_cdr_conv_HakoBatteryStatus import *
from ..geometry_msgs.pdu_cdr_conv_Point import *
from ..geometry_msgs.pdu_cdr_conv_Pose import *
from ..geometry_msgs.pdu_cdr_conv_Quaternion import *



def py_to_cdr_body_DroneGetStateResponse(writer: CdrWriter, src: DroneGetStateResponse):
    writer.write_bool(src.ok)
    writer.write_bool(src.is_ready)
    py_to_cdr_body_Pose(writer, src.current_pose)
    py_to_cdr_body_HakoBatteryStatus(writer, src.battery_status)
    writer.write_string(src.mode)
    writer.write_string(src.message)


def cdr_body_to_py_DroneGetStateResponse(reader: CdrReader, dst: DroneGetStateResponse):
    dst.ok = reader.read_bool()
    dst.is_ready = reader.read_bool()
    cdr_body_to_py_Pose(reader, dst.current_pose)
    cdr_body_to_py_HakoBatteryStatus(reader, dst.battery_status)
    dst.mode = reader.read_string()
    dst.message = reader.read_string()
    return dst


def py_to_cdr_DroneGetStateResponse(src: DroneGetStateResponse) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_DroneGetStateResponse(writer, src)
    return writer.bytes()


def cdr_to_py_DroneGetStateResponse(cdr_payload) -> DroneGetStateResponse:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = DroneGetStateResponse()
    return cdr_body_to_py_DroneGetStateResponse(reader, dst)
