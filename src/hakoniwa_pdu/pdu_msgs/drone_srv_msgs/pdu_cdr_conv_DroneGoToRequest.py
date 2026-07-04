from .pdu_pytype_DroneGoToRequest import DroneGoToRequest
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..geometry_msgs.pdu_cdr_conv_Vector3 import *



def py_to_cdr_body_DroneGoToRequest(writer: CdrWriter, src: DroneGoToRequest):
    writer.write_string(src.drone_name)
    py_to_cdr_body_Vector3(writer, src.target_pose)
    writer.write_float32(src.speed_m_s)
    writer.write_float32(src.yaw_deg)
    writer.write_float32(src.tolerance_m)
    writer.write_float32(src.timeout_sec)


def cdr_body_to_py_DroneGoToRequest(reader: CdrReader, dst: DroneGoToRequest):
    dst.drone_name = reader.read_string()
    cdr_body_to_py_Vector3(reader, dst.target_pose)
    dst.speed_m_s = reader.read_float32()
    dst.yaw_deg = reader.read_float32()
    dst.tolerance_m = reader.read_float32()
    dst.timeout_sec = reader.read_float32()
    return dst


def py_to_cdr_DroneGoToRequest(src: DroneGoToRequest) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_DroneGoToRequest(writer, src)
    return writer.bytes()


def cdr_to_py_DroneGoToRequest(cdr_payload) -> DroneGoToRequest:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = DroneGoToRequest()
    return cdr_body_to_py_DroneGoToRequest(reader, dst)
