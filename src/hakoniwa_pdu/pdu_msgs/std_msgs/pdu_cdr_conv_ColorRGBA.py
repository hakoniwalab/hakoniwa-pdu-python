from .pdu_pytype_ColorRGBA import ColorRGBA
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_ColorRGBA(writer: CdrWriter, src: ColorRGBA):
    writer.write_float32(src.r)
    writer.write_float32(src.g)
    writer.write_float32(src.b)
    writer.write_float32(src.a)


def cdr_body_to_py_ColorRGBA(reader: CdrReader, dst: ColorRGBA):
    dst.r = reader.read_float32()
    dst.g = reader.read_float32()
    dst.b = reader.read_float32()
    dst.a = reader.read_float32()
    return dst


def py_to_cdr_ColorRGBA(src: ColorRGBA) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_ColorRGBA(writer, src)
    return writer.bytes()


def cdr_to_py_ColorRGBA(cdr_payload) -> ColorRGBA:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = ColorRGBA()
    return cdr_body_to_py_ColorRGBA(reader, dst)
