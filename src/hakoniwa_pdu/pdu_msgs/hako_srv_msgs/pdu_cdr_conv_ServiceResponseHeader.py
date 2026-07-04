from .pdu_pytype_ServiceResponseHeader import ServiceResponseHeader
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_ServiceResponseHeader(writer: CdrWriter, src: ServiceResponseHeader):
    writer.write_uint32(src.request_id)
    writer.write_string(src.service_name)
    writer.write_string(src.client_name)
    writer.write_uint8(src.status)
    writer.write_uint8(src.processing_percentage)
    writer.write_int32(src.result_code)


def cdr_body_to_py_ServiceResponseHeader(reader: CdrReader, dst: ServiceResponseHeader):
    dst.request_id = reader.read_uint32()
    dst.service_name = reader.read_string()
    dst.client_name = reader.read_string()
    dst.status = reader.read_uint8()
    dst.processing_percentage = reader.read_uint8()
    dst.result_code = reader.read_int32()
    return dst


def py_to_cdr_ServiceResponseHeader(src: ServiceResponseHeader) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_ServiceResponseHeader(writer, src)
    return writer.bytes()


def cdr_to_py_ServiceResponseHeader(cdr_payload) -> ServiceResponseHeader:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = ServiceResponseHeader()
    return cdr_body_to_py_ServiceResponseHeader(reader, dst)
