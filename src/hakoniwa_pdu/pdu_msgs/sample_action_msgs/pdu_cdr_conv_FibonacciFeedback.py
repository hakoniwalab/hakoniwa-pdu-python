from .pdu_pytype_FibonacciFeedback import FibonacciFeedback
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_FibonacciFeedback(writer: CdrWriter, src: FibonacciFeedback):
    writer.write_sequence_length(src.partial_sequence)
    for elem in src.partial_sequence:
        writer.write_int32(elem)


def cdr_body_to_py_FibonacciFeedback(reader: CdrReader, dst: FibonacciFeedback):
    dst.partial_sequence = [reader.read_int32() for _ in range(reader.read_uint32())]
    return dst


def py_to_cdr_FibonacciFeedback(src: FibonacciFeedback) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_FibonacciFeedback(writer, src)
    return writer.bytes()


def cdr_to_py_FibonacciFeedback(cdr_payload) -> FibonacciFeedback:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = FibonacciFeedback()
    return cdr_body_to_py_FibonacciFeedback(reader, dst)
