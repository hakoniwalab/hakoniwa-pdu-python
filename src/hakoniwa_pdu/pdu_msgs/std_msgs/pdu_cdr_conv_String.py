from .pdu_pytype_String import String
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_String(writer: CdrWriter, src: String):
    writer.write_string(src.data)


def cdr_body_to_py_String(reader: CdrReader, dst: String):
    dst.data = reader.read_string()
    return dst


def py_to_cdr_String(src: String) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_String(writer, src)
    return writer.bytes()


def cdr_to_py_String(cdr_payload) -> String:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = String()
    return cdr_body_to_py_String(reader, dst)
