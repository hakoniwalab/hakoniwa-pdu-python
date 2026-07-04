from .pdu_pytype_DroneStatus import DroneStatus
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..geometry_msgs.pdu_cdr_conv_Vector3 import *



def py_to_cdr_body_DroneStatus(writer: CdrWriter, src: DroneStatus):
    writer.write_int32(src.flight_mode)
    writer.write_int32(src.internal_state)
    py_to_cdr_body_Vector3(writer, src.propeller_wind)
    writer.write_int32(src.collided_counts)


def cdr_body_to_py_DroneStatus(reader: CdrReader, dst: DroneStatus):
    dst.flight_mode = reader.read_int32()
    dst.internal_state = reader.read_int32()
    cdr_body_to_py_Vector3(reader, dst.propeller_wind)
    dst.collided_counts = reader.read_int32()
    return dst


def py_to_cdr_DroneStatus(src: DroneStatus) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_DroneStatus(writer, src)
    return writer.bytes()


def cdr_to_py_DroneStatus(cdr_payload) -> DroneStatus:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = DroneStatus()
    return cdr_body_to_py_DroneStatus(reader, dst)
