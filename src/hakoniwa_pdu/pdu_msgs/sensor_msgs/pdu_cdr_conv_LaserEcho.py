from .pdu_pytype_LaserEcho import LaserEcho
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_LaserEcho(writer: CdrWriter, src: LaserEcho):
    writer.write_sequence_length(src.echoes)
    for elem in src.echoes:
        writer.write_float32(elem)


def cdr_body_to_py_LaserEcho(reader: CdrReader, dst: LaserEcho):
    dst.echoes = [reader.read_float32() for _ in range(reader.read_uint32())]
    return dst


def py_to_cdr_LaserEcho(src: LaserEcho) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_LaserEcho(writer, src)
    return writer.bytes()


def cdr_to_py_LaserEcho(cdr_payload) -> LaserEcho:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = LaserEcho()
    return cdr_body_to_py_LaserEcho(reader, dst)
