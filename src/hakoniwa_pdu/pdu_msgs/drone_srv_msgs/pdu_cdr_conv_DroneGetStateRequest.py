from .pdu_pytype_DroneGetStateRequest import DroneGetStateRequest
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_DroneGetStateRequest(writer: CdrWriter, src: DroneGetStateRequest):
    writer.write_string(src.drone_name)


def cdr_body_to_py_DroneGetStateRequest(reader: CdrReader, dst: DroneGetStateRequest):
    dst.drone_name = reader.read_string()
    return dst


def py_to_cdr_DroneGetStateRequest(src: DroneGetStateRequest) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_DroneGetStateRequest(writer, src)
    return writer.bytes()


def cdr_to_py_DroneGetStateRequest(cdr_payload) -> DroneGetStateRequest:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = DroneGetStateRequest()
    return cdr_body_to_py_DroneGetStateRequest(reader, dst)
