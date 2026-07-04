from .pdu_pytype_AckEventResponse import AckEventResponse
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_AckEventResponse(writer: CdrWriter, src: AckEventResponse):
    writer.write_uint32(src.ack_code)


def cdr_body_to_py_AckEventResponse(reader: CdrReader, dst: AckEventResponse):
    dst.ack_code = reader.read_uint32()
    return dst


def py_to_cdr_AckEventResponse(src: AckEventResponse) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_AckEventResponse(writer, src)
    return writer.bytes()


def cdr_to_py_AckEventResponse(cdr_payload) -> AckEventResponse:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = AckEventResponse()
    return cdr_body_to_py_AckEventResponse(reader, dst)
