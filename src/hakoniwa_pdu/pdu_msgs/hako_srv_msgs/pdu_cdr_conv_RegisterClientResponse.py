from .pdu_pytype_RegisterClientResponse import RegisterClientResponse
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_RegisterClientResponse(writer: CdrWriter, src: RegisterClientResponse):
    writer.write_uint32(src.service_id)
    writer.write_uint32(src.client_id)
    writer.write_uint32(src.request_channel_id)
    writer.write_uint32(src.response_channel_id)


def cdr_body_to_py_RegisterClientResponse(reader: CdrReader, dst: RegisterClientResponse):
    dst.service_id = reader.read_uint32()
    dst.client_id = reader.read_uint32()
    dst.request_channel_id = reader.read_uint32()
    dst.response_channel_id = reader.read_uint32()
    return dst


def py_to_cdr_RegisterClientResponse(src: RegisterClientResponse) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_RegisterClientResponse(writer, src)
    return writer.bytes()


def cdr_to_py_RegisterClientResponse(cdr_payload) -> RegisterClientResponse:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = RegisterClientResponse()
    return cdr_body_to_py_RegisterClientResponse(reader, dst)
