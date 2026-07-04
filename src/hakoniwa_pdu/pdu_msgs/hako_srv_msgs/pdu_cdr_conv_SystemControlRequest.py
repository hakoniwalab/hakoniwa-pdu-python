from .pdu_pytype_SystemControlRequest import SystemControlRequest
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_SystemControlRequest(writer: CdrWriter, src: SystemControlRequest):
    writer.write_uint32(src.opcode)


def cdr_body_to_py_SystemControlRequest(reader: CdrReader, dst: SystemControlRequest):
    dst.opcode = reader.read_uint32()
    return dst


def py_to_cdr_SystemControlRequest(src: SystemControlRequest) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_SystemControlRequest(writer, src)
    return writer.bytes()


def cdr_to_py_SystemControlRequest(cdr_payload) -> SystemControlRequest:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = SystemControlRequest()
    return cdr_body_to_py_SystemControlRequest(reader, dst)
