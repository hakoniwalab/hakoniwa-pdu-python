from .pdu_pytype_ShareObjectOwnerRequest import ShareObjectOwnerRequest
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_ShareObjectOwnerRequest(writer: CdrWriter, src: ShareObjectOwnerRequest):
    writer.write_string(src.object_name)
    writer.write_uint32(src.request_type)
    writer.write_uint32(src.new_owner_id)
    writer.write_uint64(src.request_time)


def cdr_body_to_py_ShareObjectOwnerRequest(reader: CdrReader, dst: ShareObjectOwnerRequest):
    dst.object_name = reader.read_string()
    dst.request_type = reader.read_uint32()
    dst.new_owner_id = reader.read_uint32()
    dst.request_time = reader.read_uint64()
    return dst


def py_to_cdr_ShareObjectOwnerRequest(src: ShareObjectOwnerRequest) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_ShareObjectOwnerRequest(writer, src)
    return writer.bytes()


def cdr_to_py_ShareObjectOwnerRequest(cdr_payload) -> ShareObjectOwnerRequest:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = ShareObjectOwnerRequest()
    return cdr_body_to_py_ShareObjectOwnerRequest(reader, dst)
