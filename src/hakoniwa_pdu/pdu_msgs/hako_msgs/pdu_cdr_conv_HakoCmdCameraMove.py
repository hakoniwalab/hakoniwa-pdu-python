from .pdu_pytype_HakoCmdCameraMove import HakoCmdCameraMove
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..hako_msgs.pdu_cdr_conv_HakoCmdHeader import *
from ..geometry_msgs.pdu_cdr_conv_Vector3 import *



def py_to_cdr_body_HakoCmdCameraMove(writer: CdrWriter, src: HakoCmdCameraMove):
    py_to_cdr_body_HakoCmdHeader(writer, src.header)
    writer.write_int32(src.request_id)
    py_to_cdr_body_Vector3(writer, src.angle)


def cdr_body_to_py_HakoCmdCameraMove(reader: CdrReader, dst: HakoCmdCameraMove):
    cdr_body_to_py_HakoCmdHeader(reader, dst.header)
    dst.request_id = reader.read_int32()
    cdr_body_to_py_Vector3(reader, dst.angle)
    return dst


def py_to_cdr_HakoCmdCameraMove(src: HakoCmdCameraMove) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_HakoCmdCameraMove(writer, src)
    return writer.bytes()


def cdr_to_py_HakoCmdCameraMove(cdr_payload) -> HakoCmdCameraMove:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = HakoCmdCameraMove()
    return cdr_body_to_py_HakoCmdCameraMove(reader, dst)
