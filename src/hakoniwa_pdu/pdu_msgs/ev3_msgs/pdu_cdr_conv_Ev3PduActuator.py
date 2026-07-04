from .pdu_pytype_Ev3PduActuator import Ev3PduActuator
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..ev3_msgs.pdu_cdr_conv_Ev3PduActuatorHeader import *
from ..ev3_msgs.pdu_cdr_conv_Ev3PduMotor import *



def py_to_cdr_body_Ev3PduActuator(writer: CdrWriter, src: Ev3PduActuator):
    py_to_cdr_body_Ev3PduActuatorHeader(writer, src.head)
    values = src.leds
    for i in range(1):
        writer.write_uint8(values[i] if i < len(values) else 0)
    values = src.motors
    for i in range(3):
        py_to_cdr_body_Ev3PduMotor(writer, values[i] if i < len(values) else Ev3PduMotor())
    writer.write_uint32(src.gyro_reset)


def cdr_body_to_py_Ev3PduActuator(reader: CdrReader, dst: Ev3PduActuator):
    cdr_body_to_py_Ev3PduActuatorHeader(reader, dst.head)
    dst.leds = [reader.read_uint8() for _ in range(1)]
    dst.motors = []
    for _ in range(3):
        elem = Ev3PduMotor()
        cdr_body_to_py_Ev3PduMotor(reader, elem)
        dst.motors.append(elem)
    dst.gyro_reset = reader.read_uint32()
    return dst


def py_to_cdr_Ev3PduActuator(src: Ev3PduActuator) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_Ev3PduActuator(writer, src)
    return writer.bytes()


def cdr_to_py_Ev3PduActuator(cdr_payload) -> Ev3PduActuator:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = Ev3PduActuator()
    return cdr_body_to_py_Ev3PduActuator(reader, dst)
