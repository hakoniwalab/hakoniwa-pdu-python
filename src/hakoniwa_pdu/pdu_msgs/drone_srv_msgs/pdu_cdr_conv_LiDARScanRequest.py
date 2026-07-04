from .pdu_pytype_LiDARScanRequest import LiDARScanRequest
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_LiDARScanRequest(writer: CdrWriter, src: LiDARScanRequest):
    writer.write_string(src.drone_name)


def cdr_body_to_py_LiDARScanRequest(reader: CdrReader, dst: LiDARScanRequest):
    dst.drone_name = reader.read_string()
    return dst


def py_to_cdr_LiDARScanRequest(src: LiDARScanRequest) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_LiDARScanRequest(writer, src)
    return writer.bytes()


def cdr_to_py_LiDARScanRequest(cdr_payload) -> LiDARScanRequest:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = LiDARScanRequest()
    return cdr_body_to_py_LiDARScanRequest(reader, dst)
