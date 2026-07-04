from .pdu_pytype_ShareObjectOwnerResponse import ShareObjectOwnerResponse
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_ShareObjectOwnerResponse(writer: CdrWriter, src: ShareObjectOwnerResponse):
    writer.write_string(src.object_name)
    writer.write_uint32(src.request_type)
    writer.write_uint32(src.owner_id)
    writer.write_bool(src.accepted)


def cdr_body_to_py_ShareObjectOwnerResponse(reader: CdrReader, dst: ShareObjectOwnerResponse):
    dst.object_name = reader.read_string()
    dst.request_type = reader.read_uint32()
    dst.owner_id = reader.read_uint32()
    dst.accepted = reader.read_bool()
    return dst


def py_to_cdr_ShareObjectOwnerResponse(src: ShareObjectOwnerResponse) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_ShareObjectOwnerResponse(writer, src)
    return writer.bytes()


def cdr_to_py_ShareObjectOwnerResponse(cdr_payload) -> ShareObjectOwnerResponse:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = ShareObjectOwnerResponse()
    return cdr_body_to_py_ShareObjectOwnerResponse(reader, dst)
