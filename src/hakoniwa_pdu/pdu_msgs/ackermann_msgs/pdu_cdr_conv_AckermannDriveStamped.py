from .pdu_pytype_AckermannDriveStamped import AckermannDriveStamped
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..ackermann_msgs.pdu_cdr_conv_AckermannDrive import *
from ..std_msgs.pdu_cdr_conv_Header import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *



def py_to_cdr_body_AckermannDriveStamped(writer: CdrWriter, src: AckermannDriveStamped):
    py_to_cdr_body_Header(writer, src.header)
    py_to_cdr_body_AckermannDrive(writer, src.drive)


def cdr_body_to_py_AckermannDriveStamped(reader: CdrReader, dst: AckermannDriveStamped):
    cdr_body_to_py_Header(reader, dst.header)
    cdr_body_to_py_AckermannDrive(reader, dst.drive)
    return dst


def py_to_cdr_AckermannDriveStamped(src: AckermannDriveStamped) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_AckermannDriveStamped(writer, src)
    return writer.bytes()


def cdr_to_py_AckermannDriveStamped(cdr_payload) -> AckermannDriveStamped:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = AckermannDriveStamped()
    return cdr_body_to_py_AckermannDriveStamped(reader, dst)
