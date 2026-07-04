from .pdu_pytype_SimpleVarray import SimpleVarray
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_SimpleVarray(writer: CdrWriter, src: SimpleVarray):
    writer.write_sequence_length(src.data)
    for elem in src.data:
        writer.write_int8(elem)
    values = src.fixed_array
    for i in range(10):
        writer.write_int8(values[i] if i < len(values) else 0)
    writer.write_int32(src.p_mem1)


def cdr_body_to_py_SimpleVarray(reader: CdrReader, dst: SimpleVarray):
    dst.data = [reader.read_int8() for _ in range(reader.read_uint32())]
    dst.fixed_array = [reader.read_int8() for _ in range(10)]
    dst.p_mem1 = reader.read_int32()
    return dst


def py_to_cdr_SimpleVarray(src: SimpleVarray) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_SimpleVarray(writer, src)
    return writer.bytes()


def cdr_to_py_SimpleVarray(cdr_payload) -> SimpleVarray:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = SimpleVarray()
    return cdr_body_to_py_SimpleVarray(reader, dst)
