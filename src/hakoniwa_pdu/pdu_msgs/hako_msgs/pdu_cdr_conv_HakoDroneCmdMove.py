from .pdu_pytype_HakoDroneCmdMove import HakoDroneCmdMove
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..hako_msgs.pdu_cdr_conv_HakoDroneCmdHeader import *



def py_to_cdr_body_HakoDroneCmdMove(writer: CdrWriter, src: HakoDroneCmdMove):
    py_to_cdr_body_HakoDroneCmdHeader(writer, src.header)
    writer.write_float64(src.x)
    writer.write_float64(src.y)
    writer.write_float64(src.z)
    writer.write_float64(src.speed)
    writer.write_float64(src.yaw_deg)


def cdr_body_to_py_HakoDroneCmdMove(reader: CdrReader, dst: HakoDroneCmdMove):
    cdr_body_to_py_HakoDroneCmdHeader(reader, dst.header)
    dst.x = reader.read_float64()
    dst.y = reader.read_float64()
    dst.z = reader.read_float64()
    dst.speed = reader.read_float64()
    dst.yaw_deg = reader.read_float64()
    return dst


def py_to_cdr_HakoDroneCmdMove(src: HakoDroneCmdMove) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_HakoDroneCmdMove(writer, src)
    return writer.bytes()


def cdr_to_py_HakoDroneCmdMove(cdr_payload) -> HakoDroneCmdMove:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = HakoDroneCmdMove()
    return cdr_body_to_py_HakoDroneCmdMove(reader, dst)
