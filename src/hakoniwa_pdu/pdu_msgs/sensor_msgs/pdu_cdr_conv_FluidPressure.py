from .pdu_pytype_FluidPressure import FluidPressure
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..std_msgs.pdu_cdr_conv_Header import *
from ..builtin_interfaces.pdu_cdr_conv_Time import *



def py_to_cdr_body_FluidPressure(writer: CdrWriter, src: FluidPressure):
    py_to_cdr_body_Header(writer, src.header)
    writer.write_float64(src.fluid_pressure)
    writer.write_float64(src.variance)


def cdr_body_to_py_FluidPressure(reader: CdrReader, dst: FluidPressure):
    cdr_body_to_py_Header(reader, dst.header)
    dst.fluid_pressure = reader.read_float64()
    dst.variance = reader.read_float64()
    return dst


def py_to_cdr_FluidPressure(src: FluidPressure) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_FluidPressure(writer, src)
    return writer.bytes()


def cdr_to_py_FluidPressure(cdr_payload) -> FluidPressure:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = FluidPressure()
    return cdr_body_to_py_FluidPressure(reader, dst)
