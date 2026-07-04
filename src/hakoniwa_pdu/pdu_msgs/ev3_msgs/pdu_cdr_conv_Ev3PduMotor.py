from .pdu_pytype_Ev3PduMotor import Ev3PduMotor
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_Ev3PduMotor(writer: CdrWriter, src: Ev3PduMotor):
    writer.write_int32(src.power)
    writer.write_uint32(src.stop)
    writer.write_uint32(src.reset_angle)


def cdr_body_to_py_Ev3PduMotor(reader: CdrReader, dst: Ev3PduMotor):
    dst.power = reader.read_int32()
    dst.stop = reader.read_uint32()
    dst.reset_angle = reader.read_uint32()
    return dst


def py_to_cdr_Ev3PduMotor(src: Ev3PduMotor) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_Ev3PduMotor(writer, src)
    return writer.bytes()


def cdr_to_py_Ev3PduMotor(cdr_payload) -> Ev3PduMotor:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = Ev3PduMotor()
    return cdr_body_to_py_Ev3PduMotor(reader, dst)
