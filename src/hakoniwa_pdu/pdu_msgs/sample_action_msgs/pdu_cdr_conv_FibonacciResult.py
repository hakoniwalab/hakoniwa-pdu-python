from .pdu_pytype_FibonacciResult import FibonacciResult
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_FibonacciResult(writer: CdrWriter, src: FibonacciResult):
    writer.write_sequence_length(src.sequence)
    for elem in src.sequence:
        writer.write_int32(elem)


def cdr_body_to_py_FibonacciResult(reader: CdrReader, dst: FibonacciResult):
    dst.sequence = [reader.read_int32() for _ in range(reader.read_uint32())]
    return dst


def py_to_cdr_FibonacciResult(src: FibonacciResult) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_FibonacciResult(writer, src)
    return writer.bytes()


def cdr_to_py_FibonacciResult(cdr_payload) -> FibonacciResult:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = FibonacciResult()
    return cdr_body_to_py_FibonacciResult(reader, dst)
