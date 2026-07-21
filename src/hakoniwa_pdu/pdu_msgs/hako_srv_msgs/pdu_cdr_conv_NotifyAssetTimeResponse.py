from .pdu_pytype_NotifyAssetTimeResponse import NotifyAssetTimeResponse
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_NotifyAssetTimeResponse(writer: CdrWriter, src: NotifyAssetTimeResponse):
    writer.write_uint32(src.result_code)


def cdr_body_to_py_NotifyAssetTimeResponse(reader: CdrReader, dst: NotifyAssetTimeResponse):
    dst.result_code = reader.read_uint32()
    return dst


def py_to_cdr_NotifyAssetTimeResponse(src: NotifyAssetTimeResponse) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_NotifyAssetTimeResponse(writer, src)
    return writer.bytes()


def cdr_to_py_NotifyAssetTimeResponse(cdr_payload) -> NotifyAssetTimeResponse:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = NotifyAssetTimeResponse()
    return cdr_body_to_py_NotifyAssetTimeResponse(reader, dst)
