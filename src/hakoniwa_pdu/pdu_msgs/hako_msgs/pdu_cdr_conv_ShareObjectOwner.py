from .pdu_pytype_ShareObjectOwner import ShareObjectOwner
from ..pdu_cdr_runtime import CdrReader, CdrWriter

from ..geometry_msgs.pdu_cdr_conv_Twist import *
from ..geometry_msgs.pdu_cdr_conv_Vector3 import *



def py_to_cdr_body_ShareObjectOwner(writer: CdrWriter, src: ShareObjectOwner):
    writer.write_string(src.object_name)
    writer.write_uint32(src.owner_id)
    writer.write_uint64(src.last_update)
    py_to_cdr_body_Twist(writer, src.pos)


def cdr_body_to_py_ShareObjectOwner(reader: CdrReader, dst: ShareObjectOwner):
    dst.object_name = reader.read_string()
    dst.owner_id = reader.read_uint32()
    dst.last_update = reader.read_uint64()
    cdr_body_to_py_Twist(reader, dst.pos)
    return dst


def py_to_cdr_ShareObjectOwner(src: ShareObjectOwner) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_ShareObjectOwner(writer, src)
    return writer.bytes()


def cdr_to_py_ShareObjectOwner(cdr_payload) -> ShareObjectOwner:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = ShareObjectOwner()
    return cdr_body_to_py_ShareObjectOwner(reader, dst)
