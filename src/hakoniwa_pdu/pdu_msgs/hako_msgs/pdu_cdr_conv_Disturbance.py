from .pdu_pytype_Disturbance import Disturbance
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..hako_msgs.pdu_cdr_conv_DisturbanceAtm import *
from ..hako_msgs.pdu_cdr_conv_DisturbanceBoundary import *
from ..hako_msgs.pdu_cdr_conv_DisturbanceTemperature import *
from ..hako_msgs.pdu_cdr_conv_DisturbanceUserCustom import *
from ..hako_msgs.pdu_cdr_conv_DisturbanceWind import *
from ..geometry_msgs.pdu_cdr_conv_Point import *
from ..geometry_msgs.pdu_cdr_conv_Vector3 import *



def py_to_cdr_body_Disturbance(writer: CdrWriter, src: Disturbance):
    py_to_cdr_body_DisturbanceTemperature(writer, src.d_temp)
    py_to_cdr_body_DisturbanceWind(writer, src.d_wind)
    py_to_cdr_body_DisturbanceAtm(writer, src.d_atm)
    py_to_cdr_body_DisturbanceBoundary(writer, src.d_boundary)
    writer.write_sequence_length(src.d_user_custom)
    for elem in src.d_user_custom:
        py_to_cdr_body_DisturbanceUserCustom(writer, elem)


def cdr_body_to_py_Disturbance(reader: CdrReader, dst: Disturbance):
    cdr_body_to_py_DisturbanceTemperature(reader, dst.d_temp)
    cdr_body_to_py_DisturbanceWind(reader, dst.d_wind)
    cdr_body_to_py_DisturbanceAtm(reader, dst.d_atm)
    cdr_body_to_py_DisturbanceBoundary(reader, dst.d_boundary)
    dst.d_user_custom = []
    for _ in range(reader.read_uint32()):
        elem = DisturbanceUserCustom()
        cdr_body_to_py_DisturbanceUserCustom(reader, elem)
        dst.d_user_custom.append(elem)
    return dst


def py_to_cdr_Disturbance(src: Disturbance) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_Disturbance(writer, src)
    return writer.bytes()


def cdr_to_py_Disturbance(cdr_payload) -> Disturbance:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = Disturbance()
    return cdr_body_to_py_Disturbance(reader, dst)
