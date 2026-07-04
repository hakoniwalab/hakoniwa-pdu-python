from .pdu_pytype_Ev3PduSensor import Ev3PduSensor
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..ev3_msgs.pdu_cdr_conv_Ev3PduColorSensor import *
from ..ev3_msgs.pdu_cdr_conv_Ev3PduSensorHeader import *
from ..ev3_msgs.pdu_cdr_conv_Ev3PduTouchSensor import *



def py_to_cdr_body_Ev3PduSensor(writer: CdrWriter, src: Ev3PduSensor):
    py_to_cdr_body_Ev3PduSensorHeader(writer, src.head)
    values = src.buttons
    for i in range(1):
        writer.write_uint8(values[i] if i < len(values) else 0)
    values = src.color_sensors
    for i in range(2):
        py_to_cdr_body_Ev3PduColorSensor(writer, values[i] if i < len(values) else Ev3PduColorSensor())
    values = src.touch_sensors
    for i in range(2):
        py_to_cdr_body_Ev3PduTouchSensor(writer, values[i] if i < len(values) else Ev3PduTouchSensor())
    values = src.motor_angle
    for i in range(3):
        writer.write_uint32(values[i] if i < len(values) else 0)
    writer.write_int32(src.gyro_degree)
    writer.write_int32(src.gyro_degree_rate)
    writer.write_uint32(src.sensor_ultrasonic)
    writer.write_float64(src.gps_lat)
    writer.write_float64(src.gps_lon)


def cdr_body_to_py_Ev3PduSensor(reader: CdrReader, dst: Ev3PduSensor):
    cdr_body_to_py_Ev3PduSensorHeader(reader, dst.head)
    dst.buttons = [reader.read_uint8() for _ in range(1)]
    dst.color_sensors = []
    for _ in range(2):
        elem = Ev3PduColorSensor()
        cdr_body_to_py_Ev3PduColorSensor(reader, elem)
        dst.color_sensors.append(elem)
    dst.touch_sensors = []
    for _ in range(2):
        elem = Ev3PduTouchSensor()
        cdr_body_to_py_Ev3PduTouchSensor(reader, elem)
        dst.touch_sensors.append(elem)
    dst.motor_angle = [reader.read_uint32() for _ in range(3)]
    dst.gyro_degree = reader.read_int32()
    dst.gyro_degree_rate = reader.read_int32()
    dst.sensor_ultrasonic = reader.read_uint32()
    dst.gps_lat = reader.read_float64()
    dst.gps_lon = reader.read_float64()
    return dst


def py_to_cdr_Ev3PduSensor(src: Ev3PduSensor) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_Ev3PduSensor(writer, src)
    return writer.bytes()


def cdr_to_py_Ev3PduSensor(cdr_payload) -> Ev3PduSensor:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = Ev3PduSensor()
    return cdr_body_to_py_Ev3PduSensor(reader, dst)
