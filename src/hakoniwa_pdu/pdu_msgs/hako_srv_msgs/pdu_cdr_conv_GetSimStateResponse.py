from .pdu_pytype_GetSimStateResponse import GetSimStateResponse
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_GetSimStateResponse(writer: CdrWriter, src: GetSimStateResponse):
    writer.write_uint32(src.sim_state)
    writer.write_int64(src.master_time)
    writer.write_bool(src.is_pdu_created)
    writer.write_bool(src.is_simulation_mode)
    writer.write_bool(src.is_pdu_sync_mode)


def cdr_body_to_py_GetSimStateResponse(reader: CdrReader, dst: GetSimStateResponse):
    dst.sim_state = reader.read_uint32()
    dst.master_time = reader.read_int64()
    dst.is_pdu_created = reader.read_bool()
    dst.is_simulation_mode = reader.read_bool()
    dst.is_pdu_sync_mode = reader.read_bool()
    return dst


def py_to_cdr_GetSimStateResponse(src: GetSimStateResponse) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_GetSimStateResponse(writer, src)
    return writer.bytes()


def cdr_to_py_GetSimStateResponse(cdr_payload) -> GetSimStateResponse:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = GetSimStateResponse()
    return cdr_body_to_py_GetSimStateResponse(reader, dst)
