from .pdu_pytype_ActionRequestHeader import ActionRequestHeader
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_ActionRequestHeader(writer: CdrWriter, src: ActionRequestHeader):
    writer.write_uint8(src.version)
    writer.write_uint8(src.request_kind)
    values = src.reserved
    for i in range(2):
        writer.write_uint8(values[i] if i < len(values) else 0)
    values = src.goal_id
    for i in range(16):
        writer.write_uint8(values[i] if i < len(values) else 0)


def cdr_body_to_py_ActionRequestHeader(reader: CdrReader, dst: ActionRequestHeader):
    dst.version = reader.read_uint8()
    dst.request_kind = reader.read_uint8()
    dst.reserved = [reader.read_uint8() for _ in range(2)]
    dst.goal_id = [reader.read_uint8() for _ in range(16)]
    return dst


def py_to_cdr_ActionRequestHeader(src: ActionRequestHeader) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_ActionRequestHeader(writer, src)
    return writer.bytes()


def cdr_to_py_ActionRequestHeader(cdr_payload) -> ActionRequestHeader:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = ActionRequestHeader()
    return cdr_body_to_py_ActionRequestHeader(reader, dst)
