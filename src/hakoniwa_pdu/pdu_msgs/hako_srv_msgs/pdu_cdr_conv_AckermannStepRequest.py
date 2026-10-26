from .pdu_pytype_AckermannStepRequest import AckermannStepRequest
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..ackermann_msgs.pdu_cdr_conv_AckermannDrive import *



def py_to_cdr_body_AckermannStepRequest(writer: CdrWriter, src: AckermannStepRequest):
    writer.write_uint64(src.step)
    py_to_cdr_body_AckermannDrive(writer, src.drive)


def cdr_body_to_py_AckermannStepRequest(reader: CdrReader, dst: AckermannStepRequest):
    dst.step = reader.read_uint64()
    cdr_body_to_py_AckermannDrive(reader, dst.drive)
    return dst


def py_to_cdr_AckermannStepRequest(src: AckermannStepRequest) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_AckermannStepRequest(writer, src)
    return writer.bytes()


def cdr_to_py_AckermannStepRequest(cdr_payload) -> AckermannStepRequest:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = AckermannStepRequest()
    return cdr_body_to_py_AckermannStepRequest(reader, dst)
