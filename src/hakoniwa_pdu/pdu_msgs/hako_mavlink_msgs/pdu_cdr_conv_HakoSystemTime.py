from .pdu_pytype_HakoSystemTime import HakoSystemTime
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_HakoSystemTime(writer: CdrWriter, src: HakoSystemTime):
    writer.write_uint64(src.time_unix_usec)
    writer.write_uint64(src.time_boot_ms)


def cdr_body_to_py_HakoSystemTime(reader: CdrReader, dst: HakoSystemTime):
    dst.time_unix_usec = reader.read_uint64()
    dst.time_boot_ms = reader.read_uint64()
    return dst


def py_to_cdr_HakoSystemTime(src: HakoSystemTime) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_HakoSystemTime(writer, src)
    return writer.bytes()


def cdr_to_py_HakoSystemTime(cdr_payload) -> HakoSystemTime:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = HakoSystemTime()
    return cdr_body_to_py_HakoSystemTime(reader, dst)
