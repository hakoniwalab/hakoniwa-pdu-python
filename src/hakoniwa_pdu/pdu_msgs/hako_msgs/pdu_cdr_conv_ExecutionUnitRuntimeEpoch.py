from .pdu_pytype_ExecutionUnitRuntimeEpoch import ExecutionUnitRuntimeEpoch
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_ExecutionUnitRuntimeEpoch(writer: CdrWriter, src: ExecutionUnitRuntimeEpoch):
    writer.write_sequence_length(src.epoch)
    for elem in src.epoch:
        writer.write_uint8(elem)


def cdr_body_to_py_ExecutionUnitRuntimeEpoch(reader: CdrReader, dst: ExecutionUnitRuntimeEpoch):
    dst.epoch = [reader.read_uint8() for _ in range(reader.read_uint32())]
    return dst


def py_to_cdr_ExecutionUnitRuntimeEpoch(src: ExecutionUnitRuntimeEpoch) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_ExecutionUnitRuntimeEpoch(writer, src)
    return writer.bytes()


def cdr_to_py_ExecutionUnitRuntimeEpoch(cdr_payload) -> ExecutionUnitRuntimeEpoch:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = ExecutionUnitRuntimeEpoch()
    return cdr_body_to_py_ExecutionUnitRuntimeEpoch(reader, dst)
