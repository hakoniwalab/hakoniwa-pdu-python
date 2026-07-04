from .pdu_pytype_ExecutionUnitRuntimeStatus import ExecutionUnitRuntimeStatus
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_ExecutionUnitRuntimeStatus(writer: CdrWriter, src: ExecutionUnitRuntimeStatus):
    writer.write_uint32(src.config_hash)
    writer.write_uint16(src.unit_count)
    writer.write_sequence_length(src.status)
    for elem in src.status:
        writer.write_uint8(elem)
    writer.write_sequence_length(src.epoch)
    for elem in src.epoch:
        writer.write_uint8(elem)
    writer.write_sequence_length(src.curr_owner_node_id)
    for elem in src.curr_owner_node_id:
        writer.write_uint8(elem)
    writer.write_sequence_length(src.next_owner_node_id)
    for elem in src.next_owner_node_id:
        writer.write_uint8(elem)


def cdr_body_to_py_ExecutionUnitRuntimeStatus(reader: CdrReader, dst: ExecutionUnitRuntimeStatus):
    dst.config_hash = reader.read_uint32()
    dst.unit_count = reader.read_uint16()
    dst.status = [reader.read_uint8() for _ in range(reader.read_uint32())]
    dst.epoch = [reader.read_uint8() for _ in range(reader.read_uint32())]
    dst.curr_owner_node_id = [reader.read_uint8() for _ in range(reader.read_uint32())]
    dst.next_owner_node_id = [reader.read_uint8() for _ in range(reader.read_uint32())]
    return dst


def py_to_cdr_ExecutionUnitRuntimeStatus(src: ExecutionUnitRuntimeStatus) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_ExecutionUnitRuntimeStatus(writer, src)
    return writer.bytes()


def cdr_to_py_ExecutionUnitRuntimeStatus(cdr_payload) -> ExecutionUnitRuntimeStatus:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = ExecutionUnitRuntimeStatus()
    return cdr_body_to_py_ExecutionUnitRuntimeStatus(reader, dst)
