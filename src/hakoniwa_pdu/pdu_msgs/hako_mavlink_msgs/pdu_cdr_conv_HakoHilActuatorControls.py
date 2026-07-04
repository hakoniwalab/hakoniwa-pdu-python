from .pdu_pytype_HakoHilActuatorControls import HakoHilActuatorControls
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_HakoHilActuatorControls(writer: CdrWriter, src: HakoHilActuatorControls):
    writer.write_uint64(src.time_usec)
    values = src.controls
    for i in range(16):
        writer.write_float32(values[i] if i < len(values) else 0.0)
    writer.write_uint8(src.mode)
    writer.write_uint64(src.flags)


def cdr_body_to_py_HakoHilActuatorControls(reader: CdrReader, dst: HakoHilActuatorControls):
    dst.time_usec = reader.read_uint64()
    dst.controls = [reader.read_float32() for _ in range(16)]
    dst.mode = reader.read_uint8()
    dst.flags = reader.read_uint64()
    return dst


def py_to_cdr_HakoHilActuatorControls(src: HakoHilActuatorControls) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_HakoHilActuatorControls(writer, src)
    return writer.bytes()


def cdr_to_py_HakoHilActuatorControls(cdr_payload) -> HakoHilActuatorControls:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = HakoHilActuatorControls()
    return cdr_body_to_py_HakoHilActuatorControls(reader, dst)
