from .pdu_pytype_ExecutionUnitRuntimeContext import ExecutionUnitRuntimeContext
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_ExecutionUnitRuntimeContext(writer: CdrWriter, src: ExecutionUnitRuntimeContext):
    writer.write_uint32(src.config_hash)
    writer.write_uint8(src.epoch)
    writer.write_uint8(src.owner_id)
    writer.write_sequence_length(src.context)
    for elem in src.context:
        writer.write_uint8(elem)


def cdr_body_to_py_ExecutionUnitRuntimeContext(reader: CdrReader, dst: ExecutionUnitRuntimeContext):
    dst.config_hash = reader.read_uint32()
    dst.epoch = reader.read_uint8()
    dst.owner_id = reader.read_uint8()
    dst.context = [reader.read_uint8() for _ in range(reader.read_uint32())]
    return dst


def py_to_cdr_ExecutionUnitRuntimeContext(src: ExecutionUnitRuntimeContext) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_ExecutionUnitRuntimeContext(writer, src)
    return writer.bytes()


def cdr_to_py_ExecutionUnitRuntimeContext(cdr_payload) -> ExecutionUnitRuntimeContext:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = ExecutionUnitRuntimeContext()
    return cdr_body_to_py_ExecutionUnitRuntimeContext(reader, dst)
