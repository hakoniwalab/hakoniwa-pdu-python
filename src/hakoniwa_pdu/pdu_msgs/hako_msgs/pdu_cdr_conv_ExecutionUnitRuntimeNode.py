from .pdu_pytype_ExecutionUnitRuntimeNode import ExecutionUnitRuntimeNode
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_ExecutionUnitRuntimeNode(writer: CdrWriter, src: ExecutionUnitRuntimeNode):
    writer.write_uint32(src.node_id)


def cdr_body_to_py_ExecutionUnitRuntimeNode(reader: CdrReader, dst: ExecutionUnitRuntimeNode):
    dst.node_id = reader.read_uint32()
    return dst


def py_to_cdr_ExecutionUnitRuntimeNode(src: ExecutionUnitRuntimeNode) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_ExecutionUnitRuntimeNode(writer, src)
    return writer.bytes()


def cdr_to_py_ExecutionUnitRuntimeNode(cdr_payload) -> ExecutionUnitRuntimeNode:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = ExecutionUnitRuntimeNode()
    return cdr_body_to_py_ExecutionUnitRuntimeNode(reader, dst)
