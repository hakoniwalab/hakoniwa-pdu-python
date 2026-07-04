from .pdu_pytype_RegionOfInterest import RegionOfInterest
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_RegionOfInterest(writer: CdrWriter, src: RegionOfInterest):
    writer.write_uint32(src.x_offset)
    writer.write_uint32(src.y_offset)
    writer.write_uint32(src.height)
    writer.write_uint32(src.width)
    writer.write_bool(src.do_rectify)


def cdr_body_to_py_RegionOfInterest(reader: CdrReader, dst: RegionOfInterest):
    dst.x_offset = reader.read_uint32()
    dst.y_offset = reader.read_uint32()
    dst.height = reader.read_uint32()
    dst.width = reader.read_uint32()
    dst.do_rectify = reader.read_bool()
    return dst


def py_to_cdr_RegionOfInterest(src: RegionOfInterest) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_RegionOfInterest(writer, src)
    return writer.bytes()


def cdr_to_py_RegionOfInterest(cdr_payload) -> RegionOfInterest:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = RegionOfInterest()
    return cdr_body_to_py_RegionOfInterest(reader, dst)
