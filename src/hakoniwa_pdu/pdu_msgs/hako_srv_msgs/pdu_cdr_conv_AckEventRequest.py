from .pdu_pytype_AckEventRequest import AckEventRequest
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_AckEventRequest(writer: CdrWriter, src: AckEventRequest):
    writer.write_string(src.name)
    writer.write_uint32(src.event_code)
    writer.write_uint32(src.result_code)


def cdr_body_to_py_AckEventRequest(reader: CdrReader, dst: AckEventRequest):
    dst.name = reader.read_string()
    dst.event_code = reader.read_uint32()
    dst.result_code = reader.read_uint32()
    return dst


def py_to_cdr_AckEventRequest(src: AckEventRequest) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_AckEventRequest(writer, src)
    return writer.bytes()


def cdr_to_py_AckEventRequest(cdr_payload) -> AckEventRequest:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = AckEventRequest()
    return cdr_body_to_py_AckEventRequest(reader, dst)
