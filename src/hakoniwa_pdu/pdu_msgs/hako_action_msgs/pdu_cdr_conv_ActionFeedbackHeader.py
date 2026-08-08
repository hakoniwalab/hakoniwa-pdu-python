from .pdu_pytype_ActionFeedbackHeader import ActionFeedbackHeader
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_ActionFeedbackHeader(writer: CdrWriter, src: ActionFeedbackHeader):
    writer.write_uint8(src.version)
    values = src.reserved
    for i in range(3):
        writer.write_uint8(values[i] if i < len(values) else 0)
    values = src.goal_id
    for i in range(16):
        writer.write_uint8(values[i] if i < len(values) else 0)
    writer.write_uint32(src.sequence_no)


def cdr_body_to_py_ActionFeedbackHeader(reader: CdrReader, dst: ActionFeedbackHeader):
    dst.version = reader.read_uint8()
    dst.reserved = [reader.read_uint8() for _ in range(3)]
    dst.goal_id = [reader.read_uint8() for _ in range(16)]
    dst.sequence_no = reader.read_uint32()
    return dst


def py_to_cdr_ActionFeedbackHeader(src: ActionFeedbackHeader) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_ActionFeedbackHeader(writer, src)
    return writer.bytes()


def cdr_to_py_ActionFeedbackHeader(cdr_payload) -> ActionFeedbackHeader:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = ActionFeedbackHeader()
    return cdr_body_to_py_ActionFeedbackHeader(reader, dst)
