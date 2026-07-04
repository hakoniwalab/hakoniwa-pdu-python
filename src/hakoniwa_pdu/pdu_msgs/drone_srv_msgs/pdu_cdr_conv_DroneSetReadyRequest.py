from .pdu_pytype_DroneSetReadyRequest import DroneSetReadyRequest
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_DroneSetReadyRequest(writer: CdrWriter, src: DroneSetReadyRequest):
    writer.write_string(src.drone_name)


def cdr_body_to_py_DroneSetReadyRequest(reader: CdrReader, dst: DroneSetReadyRequest):
    dst.drone_name = reader.read_string()
    return dst


def py_to_cdr_DroneSetReadyRequest(src: DroneSetReadyRequest) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_DroneSetReadyRequest(writer, src)
    return writer.bytes()


def cdr_to_py_DroneSetReadyRequest(cdr_payload) -> DroneSetReadyRequest:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = DroneSetReadyRequest()
    return cdr_body_to_py_DroneSetReadyRequest(reader, dst)
