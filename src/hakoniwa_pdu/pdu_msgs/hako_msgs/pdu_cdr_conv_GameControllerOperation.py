from .pdu_pytype_GameControllerOperation import GameControllerOperation
from ..pdu_cdr_runtime import CdrReader, CdrWriter




def py_to_cdr_body_GameControllerOperation(writer: CdrWriter, src: GameControllerOperation):
    values = src.axis
    for i in range(6):
        writer.write_float64(values[i] if i < len(values) else 0.0)
    values = src.button
    for i in range(15):
        writer.write_bool(values[i] if i < len(values) else False)


def cdr_body_to_py_GameControllerOperation(reader: CdrReader, dst: GameControllerOperation):
    dst.axis = [reader.read_float64() for _ in range(6)]
    dst.button = [reader.read_bool() for _ in range(15)]
    return dst


def py_to_cdr_GameControllerOperation(src: GameControllerOperation) -> bytes:
    writer = CdrWriter()
    writer.write_encapsulation()
    py_to_cdr_body_GameControllerOperation(writer, src)
    return writer.bytes()


def cdr_to_py_GameControllerOperation(cdr_payload) -> GameControllerOperation:
    reader = CdrReader(cdr_payload)
    reader.read_encapsulation()
    dst = GameControllerOperation()
    return cdr_body_to_py_GameControllerOperation(reader, dst)
