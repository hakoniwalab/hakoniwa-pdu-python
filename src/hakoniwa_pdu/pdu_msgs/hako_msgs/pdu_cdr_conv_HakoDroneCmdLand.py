from .pdu_pytype_HakoDroneCmdLand import HakoDroneCmdLand
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..hako_msgs.pdu_cdr_conv_HakoDroneCmdHeader import *



def py_to_cdr_body_HakoDroneCmdLand(writer: CdrWriter, src: HakoDroneCmdLand):
    py_to_cdr_body_HakoDroneCmdHeader(writer, src.header)
    writer.write_float64(src.height)
    writer.write_float64(src.speed)
    writer.write_float64(src.yaw_deg)


def cdr_body_to_py_HakoDroneCmdLand(reader: CdrReader, dst: HakoDroneCmdLand):
    cdr_body_to_py_HakoDroneCmdHeader(reader, dst.header)
    dst.height = reader.read_float64()
    dst.speed = reader.read_float64()
    dst.yaw_deg = reader.read_float64()
    return dst


def py_to_cdr_HakoDroneCmdLand(src: HakoDroneCmdLand) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_HakoDroneCmdLand(writer, src)
    return writer.bytes()


def cdr_to_py_HakoDroneCmdLand(cdr_payload) -> HakoDroneCmdLand:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = HakoDroneCmdLand()
    return cdr_body_to_py_HakoDroneCmdLand(reader, dst)
