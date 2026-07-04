from .pdu_pytype_MetaPdu import MetaPdu
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_MetaPdu(writer: CdrWriter, src: MetaPdu):
    writer.write_uint32(src.total_len)
    writer.write_uint32(src.magicno)
    writer.write_uint16(src.version)
    writer.write_uint16(src.flags)
    writer.write_uint32(src.meta_request_type)
    writer.write_uint64(src.hako_time_us)
    writer.write_uint64(src.asset_time_us)
    writer.write_uint64(src.real_time_us)
    writer.write_string(src.robot_name)
    writer.write_int32(src.channel_id)
    writer.write_uint32(src.body_len)


def cdr_body_to_py_MetaPdu(reader: CdrReader, dst: MetaPdu):
    dst.total_len = reader.read_uint32()
    dst.magicno = reader.read_uint32()
    dst.version = reader.read_uint16()
    dst.flags = reader.read_uint16()
    dst.meta_request_type = reader.read_uint32()
    dst.hako_time_us = reader.read_uint64()
    dst.asset_time_us = reader.read_uint64()
    dst.real_time_us = reader.read_uint64()
    dst.robot_name = reader.read_string()
    dst.channel_id = reader.read_int32()
    dst.body_len = reader.read_uint32()
    return dst


def py_to_cdr_MetaPdu(src: MetaPdu) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_MetaPdu(writer, src)
    return writer.bytes()


def cdr_to_py_MetaPdu(cdr_payload) -> MetaPdu:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = MetaPdu()
    return cdr_body_to_py_MetaPdu(reader, dst)
