# pdu/python/pdu_utils.py

import struct

from . import binary_io

# PDU MetaData Constants and Layout
_PDU_META_FORMAT = '<IIIII'  # Little-endian: magic, version, base_off, heap_off, total_size, reserved
_PDU_META_SIZE = struct.calcsize(_PDU_META_FORMAT)

# Use the canonical size from binary_io (already aligned)
_ALIGNED_PDU_META_SIZE = binary_io.PduMetaData.PDU_META_DATA_SIZE

# Helper for variable-length array reference structure (length and offset)
_VARRAY_REF_FORMAT = '<ii' # Little-endian: length, offset
_VARRAY_REF_SIZE = struct.calcsize(_VARRAY_REF_FORMAT)

class DynamicAllocator:
    def __init__(self, is_heap: bool):
        self.data = bytearray()
        self.offset_map = {}
        self.is_heap = is_heap

    def add(self, bytes_data, expected_offset=None, key=None):
        current_size = len(self.data)
        data_len = len(bytes_data)
        if expected_offset is not None:
            if current_size < expected_offset:
                padding = bytearray(expected_offset - current_size)
                self.data.extend(padding)
                current_size = len(self.data)
            end_offset = expected_offset + data_len
            if current_size < end_offset:
                self.data.extend(bytearray(end_offset - current_size))
            self.data[expected_offset:end_offset] = bytes_data
            offset = expected_offset
        else:
            offset = len(self.data)
            self.data.extend(bytes_data)
        #print(f"add: {bytes_data} offset: {offset} len(self.data): {len(self.data)}")
        if key:
            self.offset_map[key] = offset
        
        return offset

    def to_array(self):
        return self.data

    def size(self):
        return len(self.data)

    def get_offset(self, key):
        return self.offset_map.get(key, None)

class BinaryWriterContainer:
    def __init__(self, meta):
        self.heap_allocator = DynamicAllocator(True)
        self.meta = meta
        self.meta.set_empty()

def get_binary(type, bin, elm_size):
    if type == "string":
        buffer = bytearray(elm_size)
        buffer[:len(bin)] = bin
        return buffer
    else:
        return bin

def create_pdu(base_data: bytes, heap_data: bytes = b'') -> bytes:
    """
    Assembles the final PDU bytes from base_data and heap_data.
    """
    base_size = len(base_data)
    heap_size = len(heap_data)
    
    aligned_base_size = (base_size + 7) & ~7
    aligned_heap_size = (heap_size + 7) & ~7

    total_size = _ALIGNED_PDU_META_SIZE + aligned_base_size + aligned_heap_size
    base_offset = _ALIGNED_PDU_META_SIZE
    heap_offset = _ALIGNED_PDU_META_SIZE + aligned_base_size

    pdu_buffer = bytearray(total_size)

    # Pack MetaData
    struct.pack_into(_PDU_META_FORMAT, pdu_buffer, 0,
                     binary_io.PduMetaData.PDU_META_DATA_MAGICNO,
                     binary_io.PduMetaData.PDU_META_DATA_VERSION,
                     base_offset, heap_offset, total_size)

    # Copy BaseData
    pdu_buffer[base_offset : base_offset + base_size] = base_data

    # Copy HeapData
    if heap_size > 0:
        pdu_buffer[heap_offset : heap_offset + heap_size] = heap_data

    return bytes(pdu_buffer)

def unpack_pdu(pdu_bytes: bytes) -> (dict, bytes, bytes):
    """
    Disassembles PDU bytes into metadata, base_data, and heap_data.
    """
    if len(pdu_bytes) < _ALIGNED_PDU_META_SIZE:
        raise ValueError("PDU is too small for metadata")

    magic, version, base_off, heap_off, total_size = struct.unpack_from(_PDU_META_FORMAT, pdu_bytes, 0)

    if (magic != binary_io.PduMetaData.PDU_META_DATA_MAGICNO or
            version != binary_io.PduMetaData.PDU_META_DATA_VERSION):
        raise ValueError(f"Invalid PDU MetaData: magic={hex(magic)}, version={version}")

    metadata = {
        'magic': magic,
        'version': version,
        'base_off': base_off,
        'heap_off': heap_off,
        'total_size': total_size
    }

    base_data = pdu_bytes[base_off:heap_off]
    heap_data = pdu_bytes[heap_off:total_size]

    return metadata, base_data, heap_data
