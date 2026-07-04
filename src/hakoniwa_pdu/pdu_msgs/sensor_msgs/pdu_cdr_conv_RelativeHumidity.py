from .pdu_pytype_RelativeHumidity import RelativeHumidity
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_Header import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *



def py_to_cdr_body_RelativeHumidity(writer: CdrWriter, src: RelativeHumidity):
    py_to_cdr_body_Header(writer, src.header)
    writer.write_float64(src.relative_humidity)
    writer.write_float64(src.variance)


def cdr_body_to_py_RelativeHumidity(reader: CdrReader, dst: RelativeHumidity):
    cdr_body_to_py_Header(reader, dst.header)
    dst.relative_humidity = reader.read_float64()
    dst.variance = reader.read_float64()
    return dst


def py_to_cdr_RelativeHumidity(src: RelativeHumidity) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_RelativeHumidity(writer, src)
    return writer.bytes()


def cdr_to_py_RelativeHumidity(cdr_payload) -> RelativeHumidity:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = RelativeHumidity()
    return cdr_body_to_py_RelativeHumidity(reader, dst)
