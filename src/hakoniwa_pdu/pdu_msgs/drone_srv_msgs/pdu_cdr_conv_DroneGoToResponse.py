from .pdu_pytype_DroneGoToResponse import DroneGoToResponse
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_DroneGoToResponse(writer: CdrWriter, src: DroneGoToResponse):
    writer.write_bool(src.ok)
    writer.write_string(src.message)


def cdr_body_to_py_DroneGoToResponse(reader: CdrReader, dst: DroneGoToResponse):
    dst.ok = reader.read_bool()
    dst.message = reader.read_string()
    return dst


def py_to_cdr_DroneGoToResponse(src: DroneGoToResponse) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_DroneGoToResponse(writer, src)
    return writer.bytes()


def cdr_to_py_DroneGoToResponse(cdr_payload) -> DroneGoToResponse:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = DroneGoToResponse()
    return cdr_body_to_py_DroneGoToResponse(reader, dst)
