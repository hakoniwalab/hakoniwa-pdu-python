from .pdu_pytype_AttitudeTarget import AttitudeTarget
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_Header import *
from ..geometry_msgs.pdu_cdr_conv_Quaternion import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *
from ..geometry_msgs.pdu_cdr_conv_Vector3 import *



def py_to_cdr_body_AttitudeTarget(writer: CdrWriter, src: AttitudeTarget):
    py_to_cdr_body_Header(writer, src.header)
    writer.write_uint8(src.type_mask)
    py_to_cdr_body_Quaternion(writer, src.orientation)
    py_to_cdr_body_Vector3(writer, src.body_rate)
    writer.write_float32(src.thrust)


def cdr_body_to_py_AttitudeTarget(reader: CdrReader, dst: AttitudeTarget):
    cdr_body_to_py_Header(reader, dst.header)
    dst.type_mask = reader.read_uint8()
    cdr_body_to_py_Quaternion(reader, dst.orientation)
    cdr_body_to_py_Vector3(reader, dst.body_rate)
    dst.thrust = reader.read_float32()
    return dst


def py_to_cdr_AttitudeTarget(src: AttitudeTarget) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_AttitudeTarget(writer, src)
    return writer.bytes()


def cdr_to_py_AttitudeTarget(cdr_payload) -> AttitudeTarget:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = AttitudeTarget()
    return cdr_body_to_py_AttitudeTarget(reader, dst)
