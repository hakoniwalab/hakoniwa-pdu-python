from .pdu_pytype_DroneLandRequest import DroneLandRequest
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_DroneLandRequest(writer: CdrWriter, src: DroneLandRequest):
    writer.write_string(src.drone_name)


def cdr_body_to_py_DroneLandRequest(reader: CdrReader, dst: DroneLandRequest):
    dst.drone_name = reader.read_string()
    return dst


def py_to_cdr_DroneLandRequest(src: DroneLandRequest) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_DroneLandRequest(writer, src)
    return writer.bytes()


def cdr_to_py_DroneLandRequest(cdr_payload) -> DroneLandRequest:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = DroneLandRequest()
    return cdr_body_to_py_DroneLandRequest(reader, dst)
