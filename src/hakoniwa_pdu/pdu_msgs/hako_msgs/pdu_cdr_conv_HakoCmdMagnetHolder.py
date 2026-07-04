from .pdu_pytype_HakoCmdMagnetHolder import HakoCmdMagnetHolder
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..hako_msgs.pdu_cdr_conv_HakoCmdHeader import *



def py_to_cdr_body_HakoCmdMagnetHolder(writer: CdrWriter, src: HakoCmdMagnetHolder):
    py_to_cdr_body_HakoCmdHeader(writer, src.header)
    writer.write_bool(src.magnet_on)


def cdr_body_to_py_HakoCmdMagnetHolder(reader: CdrReader, dst: HakoCmdMagnetHolder):
    cdr_body_to_py_HakoCmdHeader(reader, dst.header)
    dst.magnet_on = reader.read_bool()
    return dst


def py_to_cdr_HakoCmdMagnetHolder(src: HakoCmdMagnetHolder) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_HakoCmdMagnetHolder(writer, src)
    return writer.bytes()


def cdr_to_py_HakoCmdMagnetHolder(cdr_payload) -> HakoCmdMagnetHolder:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = HakoCmdMagnetHolder()
    return cdr_body_to_py_HakoCmdMagnetHolder(reader, dst)
