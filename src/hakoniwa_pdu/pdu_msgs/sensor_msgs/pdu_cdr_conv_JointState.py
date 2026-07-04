from .pdu_pytype_JointState import JointState
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_Header import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *



def py_to_cdr_body_JointState(writer: CdrWriter, src: JointState):
    py_to_cdr_body_Header(writer, src.header)
    writer.write_sequence_length(src.name)
    for elem in src.name:
        writer.write_string(elem)
    writer.write_sequence_length(src.position)
    for elem in src.position:
        writer.write_float64(elem)
    writer.write_sequence_length(src.velocity)
    for elem in src.velocity:
        writer.write_float64(elem)
    writer.write_sequence_length(src.effort)
    for elem in src.effort:
        writer.write_float64(elem)


def cdr_body_to_py_JointState(reader: CdrReader, dst: JointState):
    cdr_body_to_py_Header(reader, dst.header)
    dst.name = [reader.read_string() for _ in range(reader.read_uint32())]
    dst.position = [reader.read_float64() for _ in range(reader.read_uint32())]
    dst.velocity = [reader.read_float64() for _ in range(reader.read_uint32())]
    dst.effort = [reader.read_float64() for _ in range(reader.read_uint32())]
    return dst


def py_to_cdr_JointState(src: JointState) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_JointState(writer, src)
    return writer.bytes()


def cdr_to_py_JointState(cdr_payload) -> JointState:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = JointState()
    return cdr_body_to_py_JointState(reader, dst)
