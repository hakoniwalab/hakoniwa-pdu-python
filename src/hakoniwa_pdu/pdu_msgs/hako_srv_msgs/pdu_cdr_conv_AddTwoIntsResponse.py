from .pdu_pytype_AddTwoIntsResponse import AddTwoIntsResponse
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_AddTwoIntsResponse(writer: CdrWriter, src: AddTwoIntsResponse):
    writer.write_int64(src.sum)


def cdr_body_to_py_AddTwoIntsResponse(reader: CdrReader, dst: AddTwoIntsResponse):
    dst.sum = reader.read_int64()
    return dst


def py_to_cdr_AddTwoIntsResponse(src: AddTwoIntsResponse) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_AddTwoIntsResponse(writer, src)
    return writer.bytes()


def cdr_to_py_AddTwoIntsResponse(cdr_payload) -> AddTwoIntsResponse:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = AddTwoIntsResponse()
    return cdr_body_to_py_AddTwoIntsResponse(reader, dst)
