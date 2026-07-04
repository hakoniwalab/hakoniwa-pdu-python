from .pdu_pytype_HakoCameraData import HakoCameraData
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..sensor_msgs.pdu_cdr_conv_CompressedImage import *
from ..std_msgs.pdu_cdr_conv_Header import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *



def py_to_cdr_body_HakoCameraData(writer: CdrWriter, src: HakoCameraData):
    writer.write_int32(src.request_id)
    py_to_cdr_body_CompressedImage(writer, src.image)


def cdr_body_to_py_HakoCameraData(reader: CdrReader, dst: HakoCameraData):
    dst.request_id = reader.read_int32()
    cdr_body_to_py_CompressedImage(reader, dst.image)
    return dst


def py_to_cdr_HakoCameraData(src: HakoCameraData) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_HakoCameraData(writer, src)
    return writer.bytes()


def cdr_to_py_HakoCameraData(cdr_payload) -> HakoCameraData:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = HakoCameraData()
    return cdr_body_to_py_HakoCameraData(reader, dst)
