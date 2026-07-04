from .pdu_pytype_BatteryState import BatteryState
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_Header import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *



def py_to_cdr_body_BatteryState(writer: CdrWriter, src: BatteryState):
    py_to_cdr_body_Header(writer, src.header)
    writer.write_float32(src.voltage)
    writer.write_float32(src.temperature)
    writer.write_float32(src.current)
    writer.write_float32(src.charge)
    writer.write_float32(src.capacity)
    writer.write_float32(src.design_capacity)
    writer.write_float32(src.percentage)
    writer.write_uint8(src.power_supply_status)
    writer.write_uint8(src.power_supply_health)
    writer.write_uint8(src.power_supply_technology)
    writer.write_bool(src.present)
    writer.write_sequence_length(src.cell_voltage)
    for elem in src.cell_voltage:
        writer.write_float32(elem)
    writer.write_sequence_length(src.cell_temperature)
    for elem in src.cell_temperature:
        writer.write_float32(elem)
    writer.write_string(src.location)
    writer.write_string(src.serial_number)


def cdr_body_to_py_BatteryState(reader: CdrReader, dst: BatteryState):
    cdr_body_to_py_Header(reader, dst.header)
    dst.voltage = reader.read_float32()
    dst.temperature = reader.read_float32()
    dst.current = reader.read_float32()
    dst.charge = reader.read_float32()
    dst.capacity = reader.read_float32()
    dst.design_capacity = reader.read_float32()
    dst.percentage = reader.read_float32()
    dst.power_supply_status = reader.read_uint8()
    dst.power_supply_health = reader.read_uint8()
    dst.power_supply_technology = reader.read_uint8()
    dst.present = reader.read_bool()
    dst.cell_voltage = [reader.read_float32() for _ in range(reader.read_uint32())]
    dst.cell_temperature = [reader.read_float32() for _ in range(reader.read_uint32())]
    dst.location = reader.read_string()
    dst.serial_number = reader.read_string()
    return dst


def py_to_cdr_BatteryState(src: BatteryState) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_BatteryState(writer, src)
    return writer.bytes()


def cdr_to_py_BatteryState(cdr_payload) -> BatteryState:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = BatteryState()
    return cdr_body_to_py_BatteryState(reader, dst)
