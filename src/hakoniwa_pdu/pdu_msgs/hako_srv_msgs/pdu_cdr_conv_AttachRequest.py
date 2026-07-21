from .pdu_pytype_AttachRequest import AttachRequest
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_AttachRequest(writer: CdrWriter, src: AttachRequest):
    writer.write_string(src.asset_name)
    writer.write_uint64(src.delta_asset_tick)


def cdr_body_to_py_AttachRequest(reader: CdrReader, dst: AttachRequest):
    dst.asset_name = reader.read_string()
    dst.delta_asset_tick = reader.read_uint64()
    return dst


def py_to_cdr_AttachRequest(src: AttachRequest) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_AttachRequest(writer, src)
    return writer.bytes()


def cdr_to_py_AttachRequest(cdr_payload) -> AttachRequest:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = AttachRequest()
    return cdr_body_to_py_AttachRequest(reader, dst)
