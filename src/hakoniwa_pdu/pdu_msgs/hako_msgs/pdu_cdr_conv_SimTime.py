from .pdu_pytype_SimTime import SimTime
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_SimTime(writer: CdrWriter, src: SimTime):
    writer.write_uint64(src.time_usec)


def cdr_body_to_py_SimTime(reader: CdrReader, dst: SimTime):
    dst.time_usec = reader.read_uint64()
    return dst


def py_to_cdr_SimTime(src: SimTime) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_SimTime(writer, src)
    return writer.bytes()


def cdr_to_py_SimTime(cdr_payload) -> SimTime:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = SimTime()
    return cdr_body_to_py_SimTime(reader, dst)
