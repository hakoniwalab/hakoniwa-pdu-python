from .pdu_pytype_ChannelFloat32 import ChannelFloat32
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_ChannelFloat32(writer: CdrWriter, src: ChannelFloat32):
    writer.write_string(src.name)
    writer.write_sequence_length(src.values)
    for elem in src.values:
        writer.write_float32(elem)


def cdr_body_to_py_ChannelFloat32(reader: CdrReader, dst: ChannelFloat32):
    dst.name = reader.read_string()
    dst.values = [reader.read_float32() for _ in range(reader.read_uint32())]
    return dst


def py_to_cdr_ChannelFloat32(src: ChannelFloat32) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_ChannelFloat32(writer, src)
    return writer.bytes()


def cdr_to_py_ChannelFloat32(cdr_payload) -> ChannelFloat32:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = ChannelFloat32()
    return cdr_body_to_py_ChannelFloat32(reader, dst)
