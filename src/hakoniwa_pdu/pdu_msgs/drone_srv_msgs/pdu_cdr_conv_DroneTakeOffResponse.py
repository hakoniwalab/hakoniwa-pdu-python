from .pdu_pytype_DroneTakeOffResponse import DroneTakeOffResponse
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_DroneTakeOffResponse(writer: CdrWriter, src: DroneTakeOffResponse):
    writer.write_bool(src.ok)
    writer.write_string(src.message)


def cdr_body_to_py_DroneTakeOffResponse(reader: CdrReader, dst: DroneTakeOffResponse):
    dst.ok = reader.read_bool()
    dst.message = reader.read_string()
    return dst


def py_to_cdr_DroneTakeOffResponse(src: DroneTakeOffResponse) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_DroneTakeOffResponse(writer, src)
    return writer.bytes()


def cdr_to_py_DroneTakeOffResponse(cdr_payload) -> DroneTakeOffResponse:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = DroneTakeOffResponse()
    return cdr_body_to_py_DroneTakeOffResponse(reader, dst)
