from .pdu_pytype_DroneVisualStateArray import DroneVisualStateArray
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..hako_msgs.pdu_cdr_conv_DroneVisualState import *



def py_to_cdr_body_DroneVisualStateArray(writer: CdrWriter, src: DroneVisualStateArray):
    writer.write_uint32(src.sequence_id)
    writer.write_uint32(src.chunk_index)
    writer.write_uint32(src.chunk_count)
    writer.write_uint32(src.start_index)
    writer.write_uint32(src.valid_count)
    writer.write_sequence_length(src.drones)
    for elem in src.drones:
        py_to_cdr_body_DroneVisualState(writer, elem)


def cdr_body_to_py_DroneVisualStateArray(reader: CdrReader, dst: DroneVisualStateArray):
    dst.sequence_id = reader.read_uint32()
    dst.chunk_index = reader.read_uint32()
    dst.chunk_count = reader.read_uint32()
    dst.start_index = reader.read_uint32()
    dst.valid_count = reader.read_uint32()
    dst.drones = []
    for _ in range(reader.read_uint32()):
        elem = DroneVisualState()
        cdr_body_to_py_DroneVisualState(reader, elem)
        dst.drones.append(elem)
    return dst


def py_to_cdr_DroneVisualStateArray(src: DroneVisualStateArray) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_DroneVisualStateArray(writer, src)
    return writer.bytes()


def cdr_to_py_DroneVisualStateArray(cdr_payload) -> DroneVisualStateArray:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = DroneVisualStateArray()
    return cdr_body_to_py_DroneVisualStateArray(reader, dst)
