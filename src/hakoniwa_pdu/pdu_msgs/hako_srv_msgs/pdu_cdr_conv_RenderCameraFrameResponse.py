from .pdu_pytype_RenderCameraFrameResponse import RenderCameraFrameResponse
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_Header import *
from ..sensor_msgs.pdu_cdr_conv_Image import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *



def py_to_cdr_body_RenderCameraFrameResponse(writer: CdrWriter, src: RenderCameraFrameResponse):
    writer.write_uint32(src.result_code)
    writer.write_uint64(src.sim_time_usec)
    py_to_cdr_body_Image(writer, src.rgb)
    py_to_cdr_body_Image(writer, src.depth)
    py_to_cdr_body_Image(writer, src.segmentation)


def cdr_body_to_py_RenderCameraFrameResponse(reader: CdrReader, dst: RenderCameraFrameResponse):
    dst.result_code = reader.read_uint32()
    dst.sim_time_usec = reader.read_uint64()
    cdr_body_to_py_Image(reader, dst.rgb)
    cdr_body_to_py_Image(reader, dst.depth)
    cdr_body_to_py_Image(reader, dst.segmentation)
    return dst


def py_to_cdr_RenderCameraFrameResponse(src: RenderCameraFrameResponse) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_RenderCameraFrameResponse(writer, src)
    return writer.bytes()


def cdr_to_py_RenderCameraFrameResponse(cdr_payload) -> RenderCameraFrameResponse:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = RenderCameraFrameResponse()
    return cdr_body_to_py_RenderCameraFrameResponse(reader, dst)
