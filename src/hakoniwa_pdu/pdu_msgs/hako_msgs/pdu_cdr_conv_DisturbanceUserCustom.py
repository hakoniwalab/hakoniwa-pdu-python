from .pdu_pytype_DisturbanceUserCustom import DisturbanceUserCustom
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_DisturbanceUserCustom(writer: CdrWriter, src: DisturbanceUserCustom):
    writer.write_sequence_length(src.data)
    for elem in src.data:
        writer.write_float64(elem)


def cdr_body_to_py_DisturbanceUserCustom(reader: CdrReader, dst: DisturbanceUserCustom):
    dst.data = [reader.read_float64() for _ in range(reader.read_uint32())]
    return dst


def py_to_cdr_DisturbanceUserCustom(src: DisturbanceUserCustom) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_DisturbanceUserCustom(writer, src)
    return writer.bytes()


def cdr_to_py_DisturbanceUserCustom(cdr_payload) -> DisturbanceUserCustom:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = DisturbanceUserCustom()
    return cdr_body_to_py_DisturbanceUserCustom(reader, dst)
