from .pdu_pytype_Time import Time
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_Time(writer: CdrWriter, src: Time):
    writer.write_int32(src.sec)
    writer.write_uint32(src.nanosec)


def cdr_body_to_py_Time(reader: CdrReader, dst: Time):
    dst.sec = reader.read_int32()
    dst.nanosec = reader.read_uint32()
    return dst


def py_to_cdr_Time(src: Time) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_Time(writer, src)
    return writer.bytes()


def cdr_to_py_Time(cdr_payload) -> Time:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = Time()
    return cdr_body_to_py_Time(reader, dst)
