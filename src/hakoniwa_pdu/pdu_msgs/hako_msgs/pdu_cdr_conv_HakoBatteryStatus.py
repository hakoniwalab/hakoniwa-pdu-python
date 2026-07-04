from .pdu_pytype_HakoBatteryStatus import HakoBatteryStatus
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_HakoBatteryStatus(writer: CdrWriter, src: HakoBatteryStatus):
    writer.write_float64(src.full_voltage)
    writer.write_float64(src.curr_voltage)
    writer.write_float64(src.curr_temp)
    writer.write_uint32(src.status)
    writer.write_uint32(src.cycles)


def cdr_body_to_py_HakoBatteryStatus(reader: CdrReader, dst: HakoBatteryStatus):
    dst.full_voltage = reader.read_float64()
    dst.curr_voltage = reader.read_float64()
    dst.curr_temp = reader.read_float64()
    dst.status = reader.read_uint32()
    dst.cycles = reader.read_uint32()
    return dst


def py_to_cdr_HakoBatteryStatus(src: HakoBatteryStatus) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_HakoBatteryStatus(writer, src)
    return writer.bytes()


def cdr_to_py_HakoBatteryStatus(cdr_payload) -> HakoBatteryStatus:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = HakoBatteryStatus()
    return cdr_body_to_py_HakoBatteryStatus(reader, dst)
