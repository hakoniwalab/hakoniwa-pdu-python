from .pdu_pytype_ActionResponseHeader import ActionResponseHeader
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_ActionResponseHeader(writer: CdrWriter, src: ActionResponseHeader):
    writer.write_uint8(src.version)
    writer.write_uint8(src.response_kind)
    writer.write_uint8(src.status)
    writer.write_uint8(src.reserved)
    values = src.goal_id
    for i in range(16):
        writer.write_uint8(values[i] if i < len(values) else 0)


def cdr_body_to_py_ActionResponseHeader(reader: CdrReader, dst: ActionResponseHeader):
    dst.version = reader.read_uint8()
    dst.response_kind = reader.read_uint8()
    dst.status = reader.read_uint8()
    dst.reserved = reader.read_uint8()
    dst.goal_id = [reader.read_uint8() for _ in range(16)]
    return dst


def py_to_cdr_ActionResponseHeader(src: ActionResponseHeader) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_ActionResponseHeader(writer, src)
    return writer.bytes()


def cdr_to_py_ActionResponseHeader(cdr_payload) -> ActionResponseHeader:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = ActionResponseHeader()
    return cdr_body_to_py_ActionResponseHeader(reader, dst)
