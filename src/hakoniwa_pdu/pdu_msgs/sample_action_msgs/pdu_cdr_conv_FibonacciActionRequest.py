from .pdu_pytype_FibonacciActionRequest import FibonacciActionRequest
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..hako_action_msgs.pdu_cdr_conv_ActionRequestHeader import *
from ..sample_action_msgs.pdu_cdr_conv_FibonacciGoal import *



def py_to_cdr_body_FibonacciActionRequest(writer: CdrWriter, src: FibonacciActionRequest):
    py_to_cdr_body_ActionRequestHeader(writer, src.header)
    py_to_cdr_body_FibonacciGoal(writer, src.body)


def cdr_body_to_py_FibonacciActionRequest(reader: CdrReader, dst: FibonacciActionRequest):
    cdr_body_to_py_ActionRequestHeader(reader, dst.header)
    cdr_body_to_py_FibonacciGoal(reader, dst.body)
    return dst


def py_to_cdr_FibonacciActionRequest(src: FibonacciActionRequest) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_FibonacciActionRequest(writer, src)
    return writer.bytes()


def cdr_to_py_FibonacciActionRequest(cdr_payload) -> FibonacciActionRequest:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = FibonacciActionRequest()
    return cdr_body_to_py_FibonacciActionRequest(reader, dst)
