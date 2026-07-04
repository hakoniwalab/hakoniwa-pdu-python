from .pdu_pytype_MagnetGrabResponse import MagnetGrabResponse
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_MagnetGrabResponse(writer: CdrWriter, src: MagnetGrabResponse):
    writer.write_bool(src.ok)
    writer.write_bool(src.magnet_on)
    writer.write_bool(src.contact_on)
    writer.write_string(src.message)


def cdr_body_to_py_MagnetGrabResponse(reader: CdrReader, dst: MagnetGrabResponse):
    dst.ok = reader.read_bool()
    dst.magnet_on = reader.read_bool()
    dst.contact_on = reader.read_bool()
    dst.message = reader.read_string()
    return dst


def py_to_cdr_MagnetGrabResponse(src: MagnetGrabResponse) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_MagnetGrabResponse(writer, src)
    return writer.bytes()


def cdr_to_py_MagnetGrabResponse(cdr_payload) -> MagnetGrabResponse:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = MagnetGrabResponse()
    return cdr_body_to_py_MagnetGrabResponse(reader, dst)
