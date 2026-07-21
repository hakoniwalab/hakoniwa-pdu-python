from .pdu_pytype_Duration import Duration
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_Duration(writer: CdrWriter, src: Duration):
    writer.write_int32(src.sec)
    writer.write_uint32(src.nanosec)


def cdr_body_to_py_Duration(reader: CdrReader, dst: Duration):
    dst.sec = reader.read_int32()
    dst.nanosec = reader.read_uint32()
    return dst


def py_to_cdr_Duration(src: Duration) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_Duration(writer, src)
    return writer.bytes()


def cdr_to_py_Duration(cdr_payload) -> Duration:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = Duration()
    return cdr_body_to_py_Duration(reader, dst)
