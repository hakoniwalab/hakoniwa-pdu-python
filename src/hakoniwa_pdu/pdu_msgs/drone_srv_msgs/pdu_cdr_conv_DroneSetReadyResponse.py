from .pdu_pytype_DroneSetReadyResponse import DroneSetReadyResponse
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_DroneSetReadyResponse(writer: CdrWriter, src: DroneSetReadyResponse):
    writer.write_bool(src.ok)
    writer.write_string(src.message)


def cdr_body_to_py_DroneSetReadyResponse(reader: CdrReader, dst: DroneSetReadyResponse):
    dst.ok = reader.read_bool()
    dst.message = reader.read_string()
    return dst


def py_to_cdr_DroneSetReadyResponse(src: DroneSetReadyResponse) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_DroneSetReadyResponse(writer, src)
    return writer.bytes()


def cdr_to_py_DroneSetReadyResponse(cdr_payload) -> DroneSetReadyResponse:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = DroneSetReadyResponse()
    return cdr_body_to_py_DroneSetReadyResponse(reader, dst)
