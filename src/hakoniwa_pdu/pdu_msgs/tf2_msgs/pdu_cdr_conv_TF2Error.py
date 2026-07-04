from .pdu_pytype_TF2Error import TF2Error
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_TF2Error(writer: CdrWriter, src: TF2Error):
    writer.write_uint8(src.error)
    writer.write_string(src.error_string)


def cdr_body_to_py_TF2Error(reader: CdrReader, dst: TF2Error):
    dst.error = reader.read_uint8()
    dst.error_string = reader.read_string()
    return dst


def py_to_cdr_TF2Error(src: TF2Error) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_TF2Error(writer, src)
    return writer.bytes()


def cdr_to_py_TF2Error(cdr_payload) -> TF2Error:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = TF2Error()
    return cdr_body_to_py_TF2Error(reader, dst)
