from .pdu_pytype_HakoCanHead import HakoCanHead
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_HakoCanHead(writer: CdrWriter, src: HakoCanHead):
    writer.write_uint32(src.channel)
    writer.write_uint32(src.ide)
    writer.write_uint32(src.rtr)
    writer.write_uint32(src.dlc)
    writer.write_uint32(src.canid)


def cdr_body_to_py_HakoCanHead(reader: CdrReader, dst: HakoCanHead):
    dst.channel = reader.read_uint32()
    dst.ide = reader.read_uint32()
    dst.rtr = reader.read_uint32()
    dst.dlc = reader.read_uint32()
    dst.canid = reader.read_uint32()
    return dst


def py_to_cdr_HakoCanHead(src: HakoCanHead) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_HakoCanHead(writer, src)
    return writer.bytes()


def cdr_to_py_HakoCanHead(cdr_payload) -> HakoCanHead:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = HakoCanHead()
    return cdr_body_to_py_HakoCanHead(reader, dst)
