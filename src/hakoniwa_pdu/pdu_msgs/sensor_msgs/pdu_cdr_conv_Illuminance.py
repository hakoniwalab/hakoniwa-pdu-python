from .pdu_pytype_Illuminance import Illuminance
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_Header import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *



def py_to_cdr_body_Illuminance(writer: CdrWriter, src: Illuminance):
    py_to_cdr_body_Header(writer, src.header)
    writer.write_float64(src.illuminance)
    writer.write_float64(src.variance)


def cdr_body_to_py_Illuminance(reader: CdrReader, dst: Illuminance):
    cdr_body_to_py_Header(reader, dst.header)
    dst.illuminance = reader.read_float64()
    dst.variance = reader.read_float64()
    return dst


def py_to_cdr_Illuminance(src: Illuminance) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_Illuminance(writer, src)
    return writer.bytes()


def cdr_to_py_Illuminance(cdr_payload) -> Illuminance:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = Illuminance()
    return cdr_body_to_py_Illuminance(reader, dst)
