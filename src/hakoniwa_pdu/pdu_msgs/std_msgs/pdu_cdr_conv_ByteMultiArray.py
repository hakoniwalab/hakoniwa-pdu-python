from .pdu_pytype_ByteMultiArray import ByteMultiArray
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_MultiArrayDimension import *
from ..std_msgs.pdu_cdr_conv_MultiArrayLayout import *



def py_to_cdr_body_ByteMultiArray(writer: CdrWriter, src: ByteMultiArray):
    py_to_cdr_body_MultiArrayLayout(writer, src.layout)
    writer.write_sequence_length(src.data)
    for elem in src.data:
        writer.write_uint8(elem)


def cdr_body_to_py_ByteMultiArray(reader: CdrReader, dst: ByteMultiArray):
    cdr_body_to_py_MultiArrayLayout(reader, dst.layout)
    dst.data = [reader.read_uint8() for _ in range(reader.read_uint32())]
    return dst


def py_to_cdr_ByteMultiArray(src: ByteMultiArray) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_ByteMultiArray(writer, src)
    return writer.bytes()


def cdr_to_py_ByteMultiArray(cdr_payload) -> ByteMultiArray:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = ByteMultiArray()
    return cdr_body_to_py_ByteMultiArray(reader, dst)
