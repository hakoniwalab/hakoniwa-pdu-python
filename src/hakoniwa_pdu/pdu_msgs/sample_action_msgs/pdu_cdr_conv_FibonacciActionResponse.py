from .pdu_pytype_FibonacciActionResponse import FibonacciActionResponse
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..hako_action_msgs.pdu_cdr_conv_ActionResponseHeader import *
from ..sample_action_msgs.pdu_cdr_conv_FibonacciResult import *



def py_to_cdr_body_FibonacciActionResponse(writer: CdrWriter, src: FibonacciActionResponse):
    py_to_cdr_body_ActionResponseHeader(writer, src.header)
    py_to_cdr_body_FibonacciResult(writer, src.body)


def cdr_body_to_py_FibonacciActionResponse(reader: CdrReader, dst: FibonacciActionResponse):
    cdr_body_to_py_ActionResponseHeader(reader, dst.header)
    cdr_body_to_py_FibonacciResult(reader, dst.body)
    return dst


def py_to_cdr_FibonacciActionResponse(src: FibonacciActionResponse) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_FibonacciActionResponse(writer, src)
    return writer.bytes()


def cdr_to_py_FibonacciActionResponse(cdr_payload) -> FibonacciActionResponse:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = FibonacciActionResponse()
    return cdr_body_to_py_FibonacciActionResponse(reader, dst)
