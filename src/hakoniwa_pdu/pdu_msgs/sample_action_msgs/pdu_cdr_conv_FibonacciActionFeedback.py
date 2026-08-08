from .pdu_pytype_FibonacciActionFeedback import FibonacciActionFeedback
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..hako_action_msgs.pdu_cdr_conv_ActionFeedbackHeader import *
from ..sample_action_msgs.pdu_cdr_conv_FibonacciFeedback import *



def py_to_cdr_body_FibonacciActionFeedback(writer: CdrWriter, src: FibonacciActionFeedback):
    py_to_cdr_body_ActionFeedbackHeader(writer, src.header)
    py_to_cdr_body_FibonacciFeedback(writer, src.body)


def cdr_body_to_py_FibonacciActionFeedback(reader: CdrReader, dst: FibonacciActionFeedback):
    cdr_body_to_py_ActionFeedbackHeader(reader, dst.header)
    cdr_body_to_py_FibonacciFeedback(reader, dst.body)
    return dst


def py_to_cdr_FibonacciActionFeedback(src: FibonacciActionFeedback) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_FibonacciActionFeedback(writer, src)
    return writer.bytes()


def cdr_to_py_FibonacciActionFeedback(cdr_payload) -> FibonacciActionFeedback:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = FibonacciActionFeedback()
    return cdr_body_to_py_FibonacciActionFeedback(reader, dst)
