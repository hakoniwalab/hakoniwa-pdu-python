from .pdu_pytype_MagnetGrabRequest import MagnetGrabRequest
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_MagnetGrabRequest(writer: CdrWriter, src: MagnetGrabRequest):
    writer.write_string(src.drone_name)
    writer.write_bool(src.grab_on)
    writer.write_float32(src.timeout_sec)


def cdr_body_to_py_MagnetGrabRequest(reader: CdrReader, dst: MagnetGrabRequest):
    dst.drone_name = reader.read_string()
    dst.grab_on = reader.read_bool()
    dst.timeout_sec = reader.read_float32()
    return dst


def py_to_cdr_MagnetGrabRequest(src: MagnetGrabRequest) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_MagnetGrabRequest(writer, src)
    return writer.bytes()


def cdr_to_py_MagnetGrabRequest(cdr_payload) -> MagnetGrabRequest:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = MagnetGrabRequest()
    return cdr_body_to_py_MagnetGrabRequest(reader, dst)
