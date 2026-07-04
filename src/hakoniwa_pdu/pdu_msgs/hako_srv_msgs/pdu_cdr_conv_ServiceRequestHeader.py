from .pdu_pytype_ServiceRequestHeader import ServiceRequestHeader
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_ServiceRequestHeader(writer: CdrWriter, src: ServiceRequestHeader):
    writer.write_uint32(src.request_id)
    writer.write_string(src.service_name)
    writer.write_string(src.client_name)
    writer.write_uint8(src.opcode)
    writer.write_int32(src.status_poll_interval_msec)


def cdr_body_to_py_ServiceRequestHeader(reader: CdrReader, dst: ServiceRequestHeader):
    dst.request_id = reader.read_uint32()
    dst.service_name = reader.read_string()
    dst.client_name = reader.read_string()
    dst.opcode = reader.read_uint8()
    dst.status_poll_interval_msec = reader.read_int32()
    return dst


def py_to_cdr_ServiceRequestHeader(src: ServiceRequestHeader) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_ServiceRequestHeader(writer, src)
    return writer.bytes()


def cdr_to_py_ServiceRequestHeader(cdr_payload) -> ServiceRequestHeader:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = ServiceRequestHeader()
    return cdr_body_to_py_ServiceRequestHeader(reader, dst)
