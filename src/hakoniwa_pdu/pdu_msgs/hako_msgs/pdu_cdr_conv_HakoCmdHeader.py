from .pdu_pytype_HakoCmdHeader import HakoCmdHeader
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_HakoCmdHeader(writer: CdrWriter, src: HakoCmdHeader):
    writer.write_bool(src.request)
    writer.write_bool(src.result)
    writer.write_int32(src.result_code)


def cdr_body_to_py_HakoCmdHeader(reader: CdrReader, dst: HakoCmdHeader):
    dst.request = reader.read_bool()
    dst.result = reader.read_bool()
    dst.result_code = reader.read_int32()
    return dst


def py_to_cdr_HakoCmdHeader(src: HakoCmdHeader) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_HakoCmdHeader(writer, src)
    return writer.bytes()


def cdr_to_py_HakoCmdHeader(cdr_payload) -> HakoCmdHeader:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = HakoCmdHeader()
    return cdr_body_to_py_HakoCmdHeader(reader, dst)
