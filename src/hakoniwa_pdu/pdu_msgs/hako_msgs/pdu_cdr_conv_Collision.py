from .pdu_pytype_Collision import Collision
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..geometry_msgs.pdu_cdr_conv_Point import *
from ..geometry_msgs.pdu_cdr_conv_Vector3 import *



def py_to_cdr_body_Collision(writer: CdrWriter, src: Collision):
    writer.write_bool(src.collision)
    writer.write_uint32(src.contact_num)
    py_to_cdr_body_Vector3(writer, src.relative_velocity)
    values = src.contact_position
    for i in range(10):
        py_to_cdr_body_Point(writer, values[i] if i < len(values) else Point())
    writer.write_float64(src.restitution_coefficient)


def cdr_body_to_py_Collision(reader: CdrReader, dst: Collision):
    dst.collision = reader.read_bool()
    dst.contact_num = reader.read_uint32()
    cdr_body_to_py_Vector3(reader, dst.relative_velocity)
    dst.contact_position = []
    for _ in range(10):
        elem = Point()
        cdr_body_to_py_Point(reader, elem)
        dst.contact_position.append(elem)
    dst.restitution_coefficient = reader.read_float64()
    return dst


def py_to_cdr_Collision(src: Collision) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_Collision(writer, src)
    return writer.bytes()


def cdr_to_py_Collision(cdr_payload) -> Collision:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = Collision()
    return cdr_body_to_py_Collision(reader, dst)
