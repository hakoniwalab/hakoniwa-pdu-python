from .pdu_pytype_HakoDroneCmdHeader import HakoDroneCmdHeader
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_HakoDroneCmdHeader(writer: CdrWriter, src: HakoDroneCmdHeader):
    writer.write_bool(src.request)
    writer.write_bool(src.result)
    writer.write_int32(src.result_code)


def cdr_body_to_py_HakoDroneCmdHeader(reader: CdrReader, dst: HakoDroneCmdHeader):
    dst.request = reader.read_bool()
    dst.result = reader.read_bool()
    dst.result_code = reader.read_int32()
    return dst


def py_to_cdr_HakoDroneCmdHeader(src: HakoDroneCmdHeader) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_HakoDroneCmdHeader(writer, src)
    return writer.bytes()


def cdr_to_py_HakoDroneCmdHeader(cdr_payload) -> HakoDroneCmdHeader:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = HakoDroneCmdHeader()
    return cdr_body_to_py_HakoDroneCmdHeader(reader, dst)
