import struct


CDR_LE_ENCAPSULATION = b"\x00\x01\x00\x00"


class CdrError(Exception):
    pass


class CdrWriter:
    def __init__(self):
        self._data = bytearray()
        self._alignment_base = 0

    def write_encapsulation(self):
        self._data.extend(CDR_LE_ENCAPSULATION)
        self._alignment_base = len(self._data)

    def bytes(self) -> bytes:
        return bytes(self._data)

    def _align(self, alignment: int):
        relative_offset = len(self._data) - self._alignment_base
        padding = (-relative_offset) % alignment
        if padding:
            self._data.extend(b"\x00" * padding)

    def _write(self, fmt: str, value, alignment: int):
        self._align(alignment)
        self._data.extend(struct.pack("<" + fmt, value))

    def write_bool(self, value):
        self._write("?", bool(value), 1)

    def write_int8(self, value):
        self._write("b", int(value), 1)

    def write_uint8(self, value):
        if isinstance(value, str):
            value = ord(value[0]) if value else 0
        self._write("B", int(value), 1)

    def write_int16(self, value):
        self._write("h", int(value), 2)

    def write_uint16(self, value):
        self._write("H", int(value), 2)

    def write_int32(self, value):
        self._write("i", int(value), 4)

    def write_uint32(self, value):
        self._write("I", int(value), 4)

    def write_int64(self, value):
        self._write("q", int(value), 8)

    def write_uint64(self, value):
        self._write("Q", int(value), 8)

    def write_float32(self, value):
        self._write("f", float(value), 4)

    def write_float64(self, value):
        self._write("d", float(value), 8)

    def write_string(self, value):
        encoded = str(value).encode("utf-8") + b"\x00"
        self.write_uint32(len(encoded))
        self._data.extend(encoded)

    def write_sequence_length(self, value):
        length = len(value)
        if length > 0xFFFFFFFF:
            raise CdrError("CDR sequence too large")
        self.write_uint32(length)


class CdrReader:
    def __init__(self, data):
        self._data = memoryview(bytes(data))
        self._offset = 0
        self._alignment_base = 0

    def read_encapsulation(self):
        if len(self._data) < 4:
            raise CdrError("CDR payload is too short for encapsulation")
        encapsulation = bytes(self._data[:4])
        if encapsulation != CDR_LE_ENCAPSULATION:
            raise CdrError(f"unsupported CDR encapsulation: {encapsulation!r}")
        self._offset = 4
        self._alignment_base = self._offset

    def _align(self, alignment: int):
        relative_offset = self._offset - self._alignment_base
        self._offset += (-relative_offset) % alignment

    def _read(self, fmt: str, alignment: int):
        self._align(alignment)
        size = struct.calcsize("<" + fmt)
        end = self._offset + size
        if end > len(self._data):
            raise CdrError("CDR payload ended unexpectedly")
        value = struct.unpack_from("<" + fmt, self._data, self._offset)[0]
        self._offset = end
        return value

    def read_bool(self):
        return bool(self._read("?", 1))

    def read_int8(self):
        return self._read("b", 1)

    def read_uint8(self):
        return self._read("B", 1)

    def read_int16(self):
        return self._read("h", 2)

    def read_uint16(self):
        return self._read("H", 2)

    def read_int32(self):
        return self._read("i", 4)

    def read_uint32(self):
        return self._read("I", 4)

    def read_int64(self):
        return self._read("q", 8)

    def read_uint64(self):
        return self._read("Q", 8)

    def read_float32(self):
        return self._read("f", 4)

    def read_float64(self):
        return self._read("d", 8)

    def read_string(self):
        length = self.read_uint32()
        end = self._offset + length
        if end > len(self._data):
            raise CdrError("CDR string ended unexpectedly")
        raw = bytes(self._data[self._offset:end])
        self._offset = end
        if raw.endswith(b"\x00"):
            raw = raw[:-1]
        return raw.decode("utf-8")
