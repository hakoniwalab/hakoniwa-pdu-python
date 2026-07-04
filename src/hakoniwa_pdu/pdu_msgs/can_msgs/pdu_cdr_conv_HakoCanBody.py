from .pdu_pytype_HakoCanBody import HakoCanBody
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_HakoCanBody(writer: CdrWriter, src: HakoCanBody):
    values = src.data
    for i in range(8):
        writer.write_uint8(values[i] if i < len(values) else 0)


def cdr_body_to_py_HakoCanBody(reader: CdrReader, dst: HakoCanBody):
    dst.data = [reader.read_uint8() for _ in range(8)]
    return dst


def py_to_cdr_HakoCanBody(src: HakoCanBody) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_HakoCanBody(writer, src)
    return writer.bytes()


def cdr_to_py_HakoCanBody(cdr_payload) -> HakoCanBody:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = HakoCanBody()
    return cdr_body_to_py_HakoCanBody(reader, dst)
