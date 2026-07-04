from .pdu_pytype_CameraInfo import CameraInfo
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_Header import *
from ..sensor_msgs.pdu_cdr_conv_RegionOfInterest import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *



def py_to_cdr_body_CameraInfo(writer: CdrWriter, src: CameraInfo):
    py_to_cdr_body_Header(writer, src.header)
    writer.write_uint32(src.height)
    writer.write_uint32(src.width)
    writer.write_string(src.distortion_model)
    writer.write_sequence_length(src.d)
    for elem in src.d:
        writer.write_float64(elem)
    values = src.k
    for i in range(9):
        writer.write_float64(values[i] if i < len(values) else 0.0)
    values = src.r
    for i in range(9):
        writer.write_float64(values[i] if i < len(values) else 0.0)
    values = src.p
    for i in range(12):
        writer.write_float64(values[i] if i < len(values) else 0.0)
    writer.write_uint32(src.binning_x)
    writer.write_uint32(src.binning_y)
    py_to_cdr_body_RegionOfInterest(writer, src.roi)


def cdr_body_to_py_CameraInfo(reader: CdrReader, dst: CameraInfo):
    cdr_body_to_py_Header(reader, dst.header)
    dst.height = reader.read_uint32()
    dst.width = reader.read_uint32()
    dst.distortion_model = reader.read_string()
    dst.d = [reader.read_float64() for _ in range(reader.read_uint32())]
    dst.k = [reader.read_float64() for _ in range(9)]
    dst.r = [reader.read_float64() for _ in range(9)]
    dst.p = [reader.read_float64() for _ in range(12)]
    dst.binning_x = reader.read_uint32()
    dst.binning_y = reader.read_uint32()
    cdr_body_to_py_RegionOfInterest(reader, dst.roi)
    return dst


def py_to_cdr_CameraInfo(src: CameraInfo) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_CameraInfo(writer, src)
    return writer.bytes()


def cdr_to_py_CameraInfo(cdr_payload) -> CameraInfo:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = CameraInfo()
    return cdr_body_to_py_CameraInfo(reader, dst)
