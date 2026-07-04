from .pdu_pytype_HakoCmdCamera import HakoCmdCamera
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..hako_msgs.pdu_cdr_conv_HakoCmdHeader import *



def py_to_cdr_body_HakoCmdCamera(writer: CdrWriter, src: HakoCmdCamera):
    py_to_cdr_body_HakoCmdHeader(writer, src.header)
    writer.write_int32(src.request_id)
    writer.write_int32(src.encode_type)


def cdr_body_to_py_HakoCmdCamera(reader: CdrReader, dst: HakoCmdCamera):
    cdr_body_to_py_HakoCmdHeader(reader, dst.header)
    dst.request_id = reader.read_int32()
    dst.encode_type = reader.read_int32()
    return dst


def py_to_cdr_HakoCmdCamera(src: HakoCmdCamera) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_HakoCmdCamera(writer, src)
    return writer.bytes()


def cdr_to_py_HakoCmdCamera(cdr_payload) -> HakoCmdCamera:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = HakoCmdCamera()
    return cdr_body_to_py_HakoCmdCamera(reader, dst)
