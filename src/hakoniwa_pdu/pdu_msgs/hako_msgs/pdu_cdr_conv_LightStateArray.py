from .pdu_pytype_LightStateArray import LightStateArray
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..hako_msgs.pdu_cdr_conv_LightState import *



def py_to_cdr_body_LightStateArray(writer: CdrWriter, src: LightStateArray):
    writer.write_uint64(src.stamp_usec)
    writer.write_string(src.carrier)
    writer.write_sequence_length(src.lights)
    for elem in src.lights:
        py_to_cdr_body_LightState(writer, elem)


def cdr_body_to_py_LightStateArray(reader: CdrReader, dst: LightStateArray):
    dst.stamp_usec = reader.read_uint64()
    dst.carrier = reader.read_string()
    dst.lights = []
    for _ in range(reader.read_uint32()):
        elem = LightState()
        cdr_body_to_py_LightState(reader, elem)
        dst.lights.append(elem)
    return dst


def py_to_cdr_LightStateArray(src: LightStateArray) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_LightStateArray(writer, src)
    return writer.bytes()


def cdr_to_py_LightStateArray(cdr_payload) -> LightStateArray:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = LightStateArray()
    return cdr_body_to_py_LightStateArray(reader, dst)
