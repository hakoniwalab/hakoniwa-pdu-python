from .pdu_pytype_JoyFeedback import JoyFeedback
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_JoyFeedback(writer: CdrWriter, src: JoyFeedback):
    writer.write_uint8(src.type)
    writer.write_uint8(src.id)
    writer.write_float32(src.intensity)


def cdr_body_to_py_JoyFeedback(reader: CdrReader, dst: JoyFeedback):
    dst.type = reader.read_uint8()
    dst.id = reader.read_uint8()
    dst.intensity = reader.read_float32()
    return dst


def py_to_cdr_JoyFeedback(src: JoyFeedback) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_JoyFeedback(writer, src)
    return writer.bytes()


def cdr_to_py_JoyFeedback(cdr_payload) -> JoyFeedback:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = JoyFeedback()
    return cdr_body_to_py_JoyFeedback(reader, dst)
