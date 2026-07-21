from .pdu_pytype_LogicalTime import LogicalTime
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_LogicalTime(writer: CdrWriter, src: LogicalTime):
    writer.write_uint64(src.generation)
    writer.write_uint64(src.offset_tick)


def cdr_body_to_py_LogicalTime(reader: CdrReader, dst: LogicalTime):
    dst.generation = reader.read_uint64()
    dst.offset_tick = reader.read_uint64()
    return dst


def py_to_cdr_LogicalTime(src: LogicalTime) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_LogicalTime(writer, src)
    return writer.bytes()


def cdr_to_py_LogicalTime(cdr_payload) -> LogicalTime:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = LogicalTime()
    return cdr_body_to_py_LogicalTime(reader, dst)
