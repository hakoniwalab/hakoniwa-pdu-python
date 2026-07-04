from .pdu_pytype_PointField import PointField
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_PointField(writer: CdrWriter, src: PointField):
    writer.write_string(src.name)
    writer.write_uint32(src.offset)
    writer.write_uint8(src.datatype)
    writer.write_uint32(src.count)


def cdr_body_to_py_PointField(reader: CdrReader, dst: PointField):
    dst.name = reader.read_string()
    dst.offset = reader.read_uint32()
    dst.datatype = reader.read_uint8()
    dst.count = reader.read_uint32()
    return dst


def py_to_cdr_PointField(src: PointField) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_PointField(writer, src)
    return writer.bytes()


def cdr_to_py_PointField(cdr_payload) -> PointField:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = PointField()
    return cdr_body_to_py_PointField(reader, dst)
