from .pdu_pytype_HakoStatusMagnetHolder import HakoStatusMagnetHolder
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_HakoStatusMagnetHolder(writer: CdrWriter, src: HakoStatusMagnetHolder):
    writer.write_bool(src.magnet_on)
    writer.write_bool(src.contact_on)


def cdr_body_to_py_HakoStatusMagnetHolder(reader: CdrReader, dst: HakoStatusMagnetHolder):
    dst.magnet_on = reader.read_bool()
    dst.contact_on = reader.read_bool()
    return dst


def py_to_cdr_HakoStatusMagnetHolder(src: HakoStatusMagnetHolder) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_HakoStatusMagnetHolder(writer, src)
    return writer.bytes()


def cdr_to_py_HakoStatusMagnetHolder(cdr_payload) -> HakoStatusMagnetHolder:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = HakoStatusMagnetHolder()
    return cdr_body_to_py_HakoStatusMagnetHolder(reader, dst)
