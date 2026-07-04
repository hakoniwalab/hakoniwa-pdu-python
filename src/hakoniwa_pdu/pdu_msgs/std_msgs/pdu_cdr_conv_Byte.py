from .pdu_pytype_Byte import Byte
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_Byte(writer: CdrWriter, src: Byte):
    writer.write_uint8(src.data)


def cdr_body_to_py_Byte(reader: CdrReader, dst: Byte):
    dst.data = reader.read_uint8()
    return dst


def py_to_cdr_Byte(src: Byte) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_Byte(writer, src)
    return writer.bytes()


def cdr_to_py_Byte(cdr_payload) -> Byte:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = Byte()
    return cdr_body_to_py_Byte(reader, dst)
