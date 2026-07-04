from .pdu_pytype_ImpulseCollision import ImpulseCollision
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..geometry_msgs.pdu_cdr_conv_Point import *
from ..geometry_msgs.pdu_cdr_conv_Vector3 import *



def py_to_cdr_body_ImpulseCollision(writer: CdrWriter, src: ImpulseCollision):
    writer.write_bool(src.collision)
    writer.write_bool(src.is_target_static)
    writer.write_float64(src.restitution_coefficient)
    py_to_cdr_body_Point(writer, src.self_contact_vector)
    py_to_cdr_body_Vector3(writer, src.normal)
    py_to_cdr_body_Point(writer, src.target_contact_vector)
    py_to_cdr_body_Vector3(writer, src.target_velocity)
    py_to_cdr_body_Vector3(writer, src.target_angular_velocity)
    py_to_cdr_body_Vector3(writer, src.target_euler)
    py_to_cdr_body_Vector3(writer, src.target_inertia)
    writer.write_float64(src.target_mass)


def cdr_body_to_py_ImpulseCollision(reader: CdrReader, dst: ImpulseCollision):
    dst.collision = reader.read_bool()
    dst.is_target_static = reader.read_bool()
    dst.restitution_coefficient = reader.read_float64()
    cdr_body_to_py_Point(reader, dst.self_contact_vector)
    cdr_body_to_py_Vector3(reader, dst.normal)
    cdr_body_to_py_Point(reader, dst.target_contact_vector)
    cdr_body_to_py_Vector3(reader, dst.target_velocity)
    cdr_body_to_py_Vector3(reader, dst.target_angular_velocity)
    cdr_body_to_py_Vector3(reader, dst.target_euler)
    cdr_body_to_py_Vector3(reader, dst.target_inertia)
    dst.target_mass = reader.read_float64()
    return dst


def py_to_cdr_ImpulseCollision(src: ImpulseCollision) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_ImpulseCollision(writer, src)
    return writer.bytes()


def cdr_to_py_ImpulseCollision(cdr_payload) -> ImpulseCollision:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = ImpulseCollision()
    return cdr_body_to_py_ImpulseCollision(reader, dst)
