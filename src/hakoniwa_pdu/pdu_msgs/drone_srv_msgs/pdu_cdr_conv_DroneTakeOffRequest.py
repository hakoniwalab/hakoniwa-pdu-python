from .pdu_pytype_DroneTakeOffRequest import DroneTakeOffRequest
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_DroneTakeOffRequest(writer: CdrWriter, src: DroneTakeOffRequest):
    writer.write_float64(src.alt_m)
    writer.write_string(src.drone_name)


def cdr_body_to_py_DroneTakeOffRequest(reader: CdrReader, dst: DroneTakeOffRequest):
    dst.alt_m = reader.read_float64()
    dst.drone_name = reader.read_string()
    return dst


def py_to_cdr_DroneTakeOffRequest(src: DroneTakeOffRequest) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_DroneTakeOffRequest(writer, src)
    return writer.bytes()


def cdr_to_py_DroneTakeOffRequest(cdr_payload) -> DroneTakeOffRequest:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = DroneTakeOffRequest()
    return cdr_body_to_py_DroneTakeOffRequest(reader, dst)
