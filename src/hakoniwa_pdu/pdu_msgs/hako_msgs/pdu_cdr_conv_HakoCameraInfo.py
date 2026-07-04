from .pdu_pytype_HakoCameraInfo import HakoCameraInfo
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..geometry_msgs.pdu_cdr_conv_Vector3 import *



def py_to_cdr_body_HakoCameraInfo(writer: CdrWriter, src: HakoCameraInfo):
    writer.write_int32(src.request_id)
    py_to_cdr_body_Vector3(writer, src.angle)


def cdr_body_to_py_HakoCameraInfo(reader: CdrReader, dst: HakoCameraInfo):
    dst.request_id = reader.read_int32()
    cdr_body_to_py_Vector3(reader, dst.angle)
    return dst


def py_to_cdr_HakoCameraInfo(src: HakoCameraInfo) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_HakoCameraInfo(writer, src)
    return writer.bytes()


def cdr_to_py_HakoCameraInfo(cdr_payload) -> HakoCameraInfo:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = HakoCameraInfo()
    return cdr_body_to_py_HakoCameraInfo(reader, dst)
