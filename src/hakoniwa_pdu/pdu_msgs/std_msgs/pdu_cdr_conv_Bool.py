from .pdu_pytype_Bool import Bool
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_Bool(writer: CdrWriter, src: Bool):
    writer.write_bool(src.data)


def cdr_body_to_py_Bool(reader: CdrReader, dst: Bool):
    dst.data = reader.read_bool()
    return dst


def py_to_cdr_Bool(src: Bool) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_Bool(writer, src)
    return writer.bytes()


def cdr_to_py_Bool(cdr_payload) -> Bool:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = Bool()
    return cdr_body_to_py_Bool(reader, dst)
