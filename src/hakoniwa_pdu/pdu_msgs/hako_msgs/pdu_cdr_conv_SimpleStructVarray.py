from .pdu_pytype_SimpleStructVarray import SimpleStructVarray
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..hako_msgs.pdu_cdr_conv_SimpleVarray import *



def py_to_cdr_body_SimpleStructVarray(writer: CdrWriter, src: SimpleStructVarray):
    writer.write_int32(src.aaa)
    values = src.fixed_str
    for i in range(2):
        writer.write_string(values[i] if i < len(values) else "")
    writer.write_sequence_length(src.varray_str)
    for elem in src.varray_str:
        writer.write_string(elem)
    values = src.fixed_array
    for i in range(5):
        py_to_cdr_body_SimpleVarray(writer, values[i] if i < len(values) else SimpleVarray())
    writer.write_sequence_length(src.data)
    for elem in src.data:
        py_to_cdr_body_SimpleVarray(writer, elem)


def cdr_body_to_py_SimpleStructVarray(reader: CdrReader, dst: SimpleStructVarray):
    dst.aaa = reader.read_int32()
    dst.fixed_str = [reader.read_string() for _ in range(2)]
    dst.varray_str = [reader.read_string() for _ in range(reader.read_uint32())]
    dst.fixed_array = []
    for _ in range(5):
        elem = SimpleVarray()
        cdr_body_to_py_SimpleVarray(reader, elem)
        dst.fixed_array.append(elem)
    dst.data = []
    for _ in range(reader.read_uint32()):
        elem = SimpleVarray()
        cdr_body_to_py_SimpleVarray(reader, elem)
        dst.data.append(elem)
    return dst


def py_to_cdr_SimpleStructVarray(src: SimpleStructVarray) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_SimpleStructVarray(writer, src)
    return writer.bytes()


def cdr_to_py_SimpleStructVarray(cdr_payload) -> SimpleStructVarray:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = SimpleStructVarray()
    return cdr_body_to_py_SimpleStructVarray(reader, dst)
