from .pdu_pytype_AddTwoIntsRequest import AddTwoIntsRequest
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_AddTwoIntsRequest(writer: CdrWriter, src: AddTwoIntsRequest):
    writer.write_int64(src.a)
    writer.write_int64(src.b)


def cdr_body_to_py_AddTwoIntsRequest(reader: CdrReader, dst: AddTwoIntsRequest):
    dst.a = reader.read_int64()
    dst.b = reader.read_int64()
    return dst


def py_to_cdr_AddTwoIntsRequest(src: AddTwoIntsRequest) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_AddTwoIntsRequest(writer, src)
    return writer.bytes()


def cdr_to_py_AddTwoIntsRequest(cdr_payload) -> AddTwoIntsRequest:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = AddTwoIntsRequest()
    return cdr_body_to_py_AddTwoIntsRequest(reader, dst)
