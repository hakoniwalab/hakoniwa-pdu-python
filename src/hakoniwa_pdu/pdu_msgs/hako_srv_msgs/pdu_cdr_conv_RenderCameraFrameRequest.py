from .pdu_pytype_RenderCameraFrameRequest import RenderCameraFrameRequest
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..geometry_msgs.pdu_cdr_conv_Point import *
from ..geometry_msgs.pdu_cdr_conv_Pose import *
from ..geometry_msgs.pdu_cdr_conv_Quaternion import *
from ..hako_srv_msgs.pdu_cdr_conv_RenderObject import *



def py_to_cdr_body_RenderCameraFrameRequest(writer: CdrWriter, src: RenderCameraFrameRequest):
    writer.write_string(src.camera_name)
    writer.write_uint64(src.sim_time_usec)
    py_to_cdr_body_Pose(writer, src.camera_pose)
    writer.write_uint8(src.outputs)
    writer.write_sequence_length(src.objects)
    for elem in src.objects:
        py_to_cdr_body_RenderObject(writer, elem)


def cdr_body_to_py_RenderCameraFrameRequest(reader: CdrReader, dst: RenderCameraFrameRequest):
    dst.camera_name = reader.read_string()
    dst.sim_time_usec = reader.read_uint64()
    cdr_body_to_py_Pose(reader, dst.camera_pose)
    dst.outputs = reader.read_uint8()
    dst.objects = []
    for _ in range(reader.read_uint32()):
        elem = RenderObject()
        cdr_body_to_py_RenderObject(reader, elem)
        dst.objects.append(elem)
    return dst


def py_to_cdr_RenderCameraFrameRequest(src: RenderCameraFrameRequest) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_RenderCameraFrameRequest(writer, src)
    return writer.bytes()


def cdr_to_py_RenderCameraFrameRequest(cdr_payload) -> RenderCameraFrameRequest:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = RenderCameraFrameRequest()
    return cdr_body_to_py_RenderCameraFrameRequest(reader, dst)
