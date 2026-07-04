from .pdu_pytype_DisturbanceAtm import DisturbanceAtm
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_DisturbanceAtm(writer: CdrWriter, src: DisturbanceAtm):
    writer.write_float64(src.sea_level_atm)


def cdr_body_to_py_DisturbanceAtm(reader: CdrReader, dst: DisturbanceAtm):
    dst.sea_level_atm = reader.read_float64()
    return dst


def py_to_cdr_DisturbanceAtm(src: DisturbanceAtm) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_DisturbanceAtm(writer, src)
    return writer.bytes()


def cdr_to_py_DisturbanceAtm(cdr_payload) -> DisturbanceAtm:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = DisturbanceAtm()
    return cdr_body_to_py_DisturbanceAtm(reader, dst)
