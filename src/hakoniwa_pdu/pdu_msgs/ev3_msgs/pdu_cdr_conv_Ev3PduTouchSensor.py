from .pdu_pytype_Ev3PduTouchSensor import Ev3PduTouchSensor
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_Ev3PduTouchSensor(writer: CdrWriter, src: Ev3PduTouchSensor):
    writer.write_uint32(src.value)


def cdr_body_to_py_Ev3PduTouchSensor(reader: CdrReader, dst: Ev3PduTouchSensor):
    dst.value = reader.read_uint32()
    return dst


def py_to_cdr_Ev3PduTouchSensor(src: Ev3PduTouchSensor) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_Ev3PduTouchSensor(writer, src)
    return writer.bytes()


def cdr_to_py_Ev3PduTouchSensor(cdr_payload) -> Ev3PduTouchSensor:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = Ev3PduTouchSensor()
    return cdr_body_to_py_Ev3PduTouchSensor(reader, dst)
