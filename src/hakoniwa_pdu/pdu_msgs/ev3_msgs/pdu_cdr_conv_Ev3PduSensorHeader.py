from .pdu_pytype_Ev3PduSensorHeader import Ev3PduSensorHeader
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_Ev3PduSensorHeader(writer: CdrWriter, src: Ev3PduSensorHeader):
    writer.write_string(src.name)
    writer.write_uint32(src.version)
    writer.write_int64(src.hakoniwa_time)
    writer.write_uint32(src.ext_off)
    writer.write_uint32(src.ext_size)


def cdr_body_to_py_Ev3PduSensorHeader(reader: CdrReader, dst: Ev3PduSensorHeader):
    dst.name = reader.read_string()
    dst.version = reader.read_uint32()
    dst.hakoniwa_time = reader.read_int64()
    dst.ext_off = reader.read_uint32()
    dst.ext_size = reader.read_uint32()
    return dst


def py_to_cdr_Ev3PduSensorHeader(src: Ev3PduSensorHeader) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_Ev3PduSensorHeader(writer, src)
    return writer.bytes()


def cdr_to_py_Ev3PduSensorHeader(cdr_payload) -> Ev3PduSensorHeader:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = Ev3PduSensorHeader()
    return cdr_body_to_py_Ev3PduSensorHeader(reader, dst)
