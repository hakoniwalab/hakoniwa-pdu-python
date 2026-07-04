from .pdu_pytype_JoyFeedbackArray import JoyFeedbackArray
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..sensor_msgs.pdu_cdr_conv_JoyFeedback import *



def py_to_cdr_body_JoyFeedbackArray(writer: CdrWriter, src: JoyFeedbackArray):
    writer.write_sequence_length(src.array)
    for elem in src.array:
        py_to_cdr_body_JoyFeedback(writer, elem)


def cdr_body_to_py_JoyFeedbackArray(reader: CdrReader, dst: JoyFeedbackArray):
    dst.array = []
    for _ in range(reader.read_uint32()):
        elem = JoyFeedback()
        cdr_body_to_py_JoyFeedback(reader, elem)
        dst.array.append(elem)
    return dst


def py_to_cdr_JoyFeedbackArray(src: JoyFeedbackArray) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_JoyFeedbackArray(writer, src)
    return writer.bytes()


def cdr_to_py_JoyFeedbackArray(cdr_payload) -> JoyFeedbackArray:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = JoyFeedbackArray()
    return cdr_body_to_py_JoyFeedbackArray(reader, dst)
