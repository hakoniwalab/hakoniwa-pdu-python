from .pdu_pytype_MultiArrayDimension import MultiArrayDimension
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_MultiArrayDimension(writer: CdrWriter, src: MultiArrayDimension):
    writer.write_string(src.label)
    writer.write_uint32(src.size)
    writer.write_uint32(src.stride)


def cdr_body_to_py_MultiArrayDimension(reader: CdrReader, dst: MultiArrayDimension):
    dst.label = reader.read_string()
    dst.size = reader.read_uint32()
    dst.stride = reader.read_uint32()
    return dst


def py_to_cdr_MultiArrayDimension(src: MultiArrayDimension) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_MultiArrayDimension(writer, src)
    return writer.bytes()


def cdr_to_py_MultiArrayDimension(cdr_payload) -> MultiArrayDimension:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = MultiArrayDimension()
    return cdr_body_to_py_MultiArrayDimension(reader, dst)
