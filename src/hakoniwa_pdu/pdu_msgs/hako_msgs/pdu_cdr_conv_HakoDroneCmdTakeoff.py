from .pdu_pytype_HakoDroneCmdTakeoff import HakoDroneCmdTakeoff
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..hako_msgs.pdu_cdr_conv_HakoDroneCmdHeader import *



def py_to_cdr_body_HakoDroneCmdTakeoff(writer: CdrWriter, src: HakoDroneCmdTakeoff):
    py_to_cdr_body_HakoDroneCmdHeader(writer, src.header)
    writer.write_float64(src.height)
    writer.write_float64(src.speed)
    writer.write_float64(src.yaw_deg)


def cdr_body_to_py_HakoDroneCmdTakeoff(reader: CdrReader, dst: HakoDroneCmdTakeoff):
    cdr_body_to_py_HakoDroneCmdHeader(reader, dst.header)
    dst.height = reader.read_float64()
    dst.speed = reader.read_float64()
    dst.yaw_deg = reader.read_float64()
    return dst


def py_to_cdr_HakoDroneCmdTakeoff(src: HakoDroneCmdTakeoff) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_HakoDroneCmdTakeoff(writer, src)
    return writer.bytes()


def cdr_to_py_HakoDroneCmdTakeoff(cdr_payload) -> HakoDroneCmdTakeoff:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = HakoDroneCmdTakeoff()
    return cdr_body_to_py_HakoDroneCmdTakeoff(reader, dst)
