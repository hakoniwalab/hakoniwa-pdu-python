from .pdu_pytype_Temperature import Temperature
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_Header import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *



def py_to_cdr_body_Temperature(writer: CdrWriter, src: Temperature):
    py_to_cdr_body_Header(writer, src.header)
    writer.write_float64(src.temperature)
    writer.write_float64(src.variance)


def cdr_body_to_py_Temperature(reader: CdrReader, dst: Temperature):
    cdr_body_to_py_Header(reader, dst.header)
    dst.temperature = reader.read_float64()
    dst.variance = reader.read_float64()
    return dst


def py_to_cdr_Temperature(src: Temperature) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_Temperature(writer, src)
    return writer.bytes()


def cdr_to_py_Temperature(cdr_payload) -> Temperature:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = Temperature()
    return cdr_body_to_py_Temperature(reader, dst)
