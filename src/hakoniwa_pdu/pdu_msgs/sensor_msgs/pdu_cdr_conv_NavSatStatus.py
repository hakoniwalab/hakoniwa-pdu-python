from .pdu_pytype_NavSatStatus import NavSatStatus
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_NavSatStatus(writer: CdrWriter, src: NavSatStatus):
    writer.write_int8(src.status)
    writer.write_uint16(src.service)


def cdr_body_to_py_NavSatStatus(reader: CdrReader, dst: NavSatStatus):
    dst.status = reader.read_int8()
    dst.service = reader.read_uint16()
    return dst


def py_to_cdr_NavSatStatus(src: NavSatStatus) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_NavSatStatus(writer, src)
    return writer.bytes()


def cdr_to_py_NavSatStatus(cdr_payload) -> NavSatStatus:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = NavSatStatus()
    return cdr_body_to_py_NavSatStatus(reader, dst)
