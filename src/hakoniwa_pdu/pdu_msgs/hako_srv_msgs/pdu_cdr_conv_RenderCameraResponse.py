from .pdu_pytype_RenderCameraResponse import RenderCameraResponse
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_Header import *
from ..sensor_msgs.pdu_cdr_conv_Image import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *



def py_to_cdr_body_RenderCameraResponse(writer: CdrWriter, src: RenderCameraResponse):
    writer.write_uint32(src.result_code)
    writer.write_uint64(src.sim_time_usec)
    py_to_cdr_body_Image(writer, src.image)


def cdr_body_to_py_RenderCameraResponse(reader: CdrReader, dst: RenderCameraResponse):
    dst.result_code = reader.read_uint32()
    dst.sim_time_usec = reader.read_uint64()
    cdr_body_to_py_Image(reader, dst.image)
    return dst


def py_to_cdr_RenderCameraResponse(src: RenderCameraResponse) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_RenderCameraResponse(writer, src)
    return writer.bytes()


def cdr_to_py_RenderCameraResponse(cdr_payload) -> RenderCameraResponse:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = RenderCameraResponse()
    return cdr_body_to_py_RenderCameraResponse(reader, dst)
