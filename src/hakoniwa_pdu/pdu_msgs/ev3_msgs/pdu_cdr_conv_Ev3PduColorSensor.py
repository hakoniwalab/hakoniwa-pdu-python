from .pdu_pytype_Ev3PduColorSensor import Ev3PduColorSensor
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_Ev3PduColorSensor(writer: CdrWriter, src: Ev3PduColorSensor):
    writer.write_uint32(src.color)
    writer.write_uint32(src.reflect)
    writer.write_uint32(src.rgb_r)
    writer.write_uint32(src.rgb_g)
    writer.write_uint32(src.rgb_b)


def cdr_body_to_py_Ev3PduColorSensor(reader: CdrReader, dst: Ev3PduColorSensor):
    dst.color = reader.read_uint32()
    dst.reflect = reader.read_uint32()
    dst.rgb_r = reader.read_uint32()
    dst.rgb_g = reader.read_uint32()
    dst.rgb_b = reader.read_uint32()
    return dst


def py_to_cdr_Ev3PduColorSensor(src: Ev3PduColorSensor) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_Ev3PduColorSensor(writer, src)
    return writer.bytes()


def cdr_to_py_Ev3PduColorSensor(cdr_payload) -> Ev3PduColorSensor:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = Ev3PduColorSensor()
    return cdr_body_to_py_Ev3PduColorSensor(reader, dst)
