from .pdu_pytype_FibonacciGoal import FibonacciGoal
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_FibonacciGoal(writer: CdrWriter, src: FibonacciGoal):
    writer.write_int32(src.order)


def cdr_body_to_py_FibonacciGoal(reader: CdrReader, dst: FibonacciGoal):
    dst.order = reader.read_int32()
    return dst


def py_to_cdr_FibonacciGoal(src: FibonacciGoal) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_FibonacciGoal(writer, src)
    return writer.bytes()


def cdr_to_py_FibonacciGoal(cdr_payload) -> FibonacciGoal:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = FibonacciGoal()
    return cdr_body_to_py_FibonacciGoal(reader, dst)
