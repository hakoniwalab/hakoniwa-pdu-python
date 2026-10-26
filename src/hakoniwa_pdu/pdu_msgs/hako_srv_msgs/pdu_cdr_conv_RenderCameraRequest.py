from .pdu_pytype_RenderCameraRequest import RenderCameraRequest
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..geometry_msgs.pdu_cdr_conv_Point import *
from ..geometry_msgs.pdu_cdr_conv_Pose import *
from ..geometry_msgs.pdu_cdr_conv_Quaternion import *



def py_to_cdr_body_RenderCameraRequest(writer: CdrWriter, src: RenderCameraRequest):
    writer.write_string(src.camera_name)
    writer.write_uint64(src.sim_time_usec)
    py_to_cdr_body_Pose(writer, src.camera_pose)


def cdr_body_to_py_RenderCameraRequest(reader: CdrReader, dst: RenderCameraRequest):
    dst.camera_name = reader.read_string()
    dst.sim_time_usec = reader.read_uint64()
    cdr_body_to_py_Pose(reader, dst.camera_pose)
    return dst


def py_to_cdr_RenderCameraRequest(src: RenderCameraRequest) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_RenderCameraRequest(writer, src)
    return writer.bytes()


def cdr_to_py_RenderCameraRequest(cdr_payload) -> RenderCameraRequest:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = RenderCameraRequest()
    return cdr_body_to_py_RenderCameraRequest(reader, dst)
