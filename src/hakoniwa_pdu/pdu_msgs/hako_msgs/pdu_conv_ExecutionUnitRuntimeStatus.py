
import struct
from .pdu_pytype_ExecutionUnitRuntimeStatus import ExecutionUnitRuntimeStatus
from ..pdu_utils import *
from .. import binary_io

# dependencies for the generated Python class



def pdu_to_py_ExecutionUnitRuntimeStatus(binary_data: bytearray) -> ExecutionUnitRuntimeStatus:
    py_obj = ExecutionUnitRuntimeStatus()
    meta_parser = binary_io.PduMetaDataParser()
    meta = meta_parser.load_pdu_meta(binary_data)
    if meta is None:
        raise ValueError("Invalid PDU binary data: MetaData not found or corrupted")
    binary_read_recursive_ExecutionUnitRuntimeStatus(meta, binary_data, py_obj, binary_io.PduMetaData.PDU_META_DATA_SIZE)
    return py_obj


def binary_read_recursive_ExecutionUnitRuntimeStatus(meta: binary_io.PduMetaData, binary_data: bytearray, py_obj: ExecutionUnitRuntimeStatus, base_off: int):
    # array_type: single 
    # data_type: primitive 
    # member_name: config_hash 
    # type_name: uint32 
    # offset: 0 size: 4 
    # array_len: 1

    
    bin = binary_io.readBinary(binary_data, base_off + 0, 4)
    py_obj.config_hash = binary_io.binTovalue("uint32", bin)
    
    # array_type: single 
    # data_type: primitive 
    # member_name: unit_count 
    # type_name: uint16 
    # offset: 4 size: 2 
    # array_len: 1

    
    bin = binary_io.readBinary(binary_data, base_off + 4, 2)
    py_obj.unit_count = binary_io.binTovalue("uint16", bin)
    
    # array_type: varray 
    # data_type: primitive 
    # member_name: status 
    # type_name: uint8 
    # offset: 8 size: 1 
    # array_len: 8

    array_size = binary_io.binTovalue("int32", binary_io.readBinary(binary_data, base_off + 8, 4))
    offset_from_heap = binary_io.binTovalue("int32", binary_io.readBinary(binary_data, base_off + 8 + 4, 4))
    one_elm_size = 1 
    array_value = binary_io.readBinary(binary_data, meta.heap_off + offset_from_heap, one_elm_size * array_size)
    
    py_obj.status = binary_io.binToArrayValues("uint8", array_value)
    
    
    # array_type: varray 
    # data_type: primitive 
    # member_name: epoch 
    # type_name: uint8 
    # offset: 16 size: 1 
    # array_len: 8

    array_size = binary_io.binTovalue("int32", binary_io.readBinary(binary_data, base_off + 16, 4))
    offset_from_heap = binary_io.binTovalue("int32", binary_io.readBinary(binary_data, base_off + 16 + 4, 4))
    one_elm_size = 1 
    array_value = binary_io.readBinary(binary_data, meta.heap_off + offset_from_heap, one_elm_size * array_size)
    
    py_obj.epoch = binary_io.binToArrayValues("uint8", array_value)
    
    
    # array_type: varray 
    # data_type: primitive 
    # member_name: curr_owner_node_id 
    # type_name: uint8 
    # offset: 24 size: 1 
    # array_len: 8

    array_size = binary_io.binTovalue("int32", binary_io.readBinary(binary_data, base_off + 24, 4))
    offset_from_heap = binary_io.binTovalue("int32", binary_io.readBinary(binary_data, base_off + 24 + 4, 4))
    one_elm_size = 1 
    array_value = binary_io.readBinary(binary_data, meta.heap_off + offset_from_heap, one_elm_size * array_size)
    
    py_obj.curr_owner_node_id = binary_io.binToArrayValues("uint8", array_value)
    
    
    # array_type: varray 
    # data_type: primitive 
    # member_name: next_owner_node_id 
    # type_name: uint8 
    # offset: 32 size: 1 
    # array_len: 8

    array_size = binary_io.binTovalue("int32", binary_io.readBinary(binary_data, base_off + 32, 4))
    offset_from_heap = binary_io.binTovalue("int32", binary_io.readBinary(binary_data, base_off + 32 + 4, 4))
    one_elm_size = 1 
    array_value = binary_io.readBinary(binary_data, meta.heap_off + offset_from_heap, one_elm_size * array_size)
    
    py_obj.next_owner_node_id = binary_io.binToArrayValues("uint8", array_value)
    
    
    return py_obj


def py_to_pdu_ExecutionUnitRuntimeStatus(py_obj: ExecutionUnitRuntimeStatus) -> bytearray:
    binary_data = bytearray()
    base_allocator = DynamicAllocator(False)
    bw_container = BinaryWriterContainer(binary_io.PduMetaData())
    binary_write_recursive_ExecutionUnitRuntimeStatus(0, bw_container, base_allocator, py_obj)

    # メタデータの設定
    total_size = base_allocator.size() + bw_container.heap_allocator.size() + binary_io.PduMetaData.PDU_META_DATA_SIZE
    bw_container.meta.total_size = total_size
    bw_container.meta.heap_off = binary_io.PduMetaData.PDU_META_DATA_SIZE + base_allocator.size()

    # binary_data のサイズを total_size に調整
    if len(binary_data) < total_size:
        binary_data.extend(bytearray(total_size - len(binary_data)))
    elif len(binary_data) > total_size:
        del binary_data[total_size:]

    # メタデータをバッファにコピー
    binary_io.writeBinary(binary_data, 0, bw_container.meta.to_bytes())

    # 基本データをバッファにコピー
    binary_io.writeBinary(binary_data, bw_container.meta.base_off, base_allocator.to_array())

    # ヒープデータをバッファにコピー
    binary_io.writeBinary(binary_data, bw_container.meta.heap_off, bw_container.heap_allocator.to_array())

    return binary_data

def binary_write_recursive_ExecutionUnitRuntimeStatus(parent_off: int, bw_container: BinaryWriterContainer, allocator, py_obj: ExecutionUnitRuntimeStatus):
    # array_type: single 
    # data_type: primitive 
    # member_name: config_hash 
    # type_name: uint32 
    # offset: 0 size: 4 
    # array_len: 1
    type = "uint32"
    off = 0

    
    bin = binary_io.typeTobin(type, py_obj.config_hash)
    bin = get_binary(type, bin, 4)
    allocator.add(bin, expected_offset=parent_off + off)
    
    # array_type: single 
    # data_type: primitive 
    # member_name: unit_count 
    # type_name: uint16 
    # offset: 4 size: 2 
    # array_len: 1
    type = "uint16"
    off = 4

    
    bin = binary_io.typeTobin(type, py_obj.unit_count)
    bin = get_binary(type, bin, 2)
    allocator.add(bin, expected_offset=parent_off + off)
    
    # array_type: varray 
    # data_type: primitive 
    # member_name: status 
    # type_name: uint8 
    # offset: 8 size: 1 
    # array_len: 8
    type = "uint8"
    off = 8

    offset_from_heap = bw_container.heap_allocator.size()
    array_size = len(py_obj.status)
    a_b = array_size.to_bytes(4, byteorder='little')
    o_b = offset_from_heap.to_bytes(4, byteorder='little')
    allocator.add(a_b + o_b, expected_offset=parent_off + off)
    binary = binary_io.typeTobin_array(type, py_obj.status, 1)
    bw_container.heap_allocator.add(binary)
    
    # array_type: varray 
    # data_type: primitive 
    # member_name: epoch 
    # type_name: uint8 
    # offset: 16 size: 1 
    # array_len: 8
    type = "uint8"
    off = 16

    offset_from_heap = bw_container.heap_allocator.size()
    array_size = len(py_obj.epoch)
    a_b = array_size.to_bytes(4, byteorder='little')
    o_b = offset_from_heap.to_bytes(4, byteorder='little')
    allocator.add(a_b + o_b, expected_offset=parent_off + off)
    binary = binary_io.typeTobin_array(type, py_obj.epoch, 1)
    bw_container.heap_allocator.add(binary)
    
    # array_type: varray 
    # data_type: primitive 
    # member_name: curr_owner_node_id 
    # type_name: uint8 
    # offset: 24 size: 1 
    # array_len: 8
    type = "uint8"
    off = 24

    offset_from_heap = bw_container.heap_allocator.size()
    array_size = len(py_obj.curr_owner_node_id)
    a_b = array_size.to_bytes(4, byteorder='little')
    o_b = offset_from_heap.to_bytes(4, byteorder='little')
    allocator.add(a_b + o_b, expected_offset=parent_off + off)
    binary = binary_io.typeTobin_array(type, py_obj.curr_owner_node_id, 1)
    bw_container.heap_allocator.add(binary)
    
    # array_type: varray 
    # data_type: primitive 
    # member_name: next_owner_node_id 
    # type_name: uint8 
    # offset: 32 size: 1 
    # array_len: 8
    type = "uint8"
    off = 32

    offset_from_heap = bw_container.heap_allocator.size()
    array_size = len(py_obj.next_owner_node_id)
    a_b = array_size.to_bytes(4, byteorder='little')
    o_b = offset_from_heap.to_bytes(4, byteorder='little')
    allocator.add(a_b + o_b, expected_offset=parent_off + off)
    binary = binary_io.typeTobin_array(type, py_obj.next_owner_node_id, 1)
    bw_container.heap_allocator.add(binary)
    

if __name__ == "__main__":
    import sys
    import json

    def print_usage():
        print(f"Usage: python -m pdu.python.pdu_conv_ExecutionUnitRuntimeStatus <read|write> [args...]")
        print(f"  read <input_binary_file> <output_json_file>")
        print(f"  write <input_json_file> <output_binary_file>")

    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    command = sys.argv[1]

    if command == "read":
        if len(sys.argv) != 4:
            print_usage()
            sys.exit(1)
        
        binary_filepath = sys.argv[2]
        output_json_filepath = sys.argv[3]

        with open(binary_filepath, "rb") as f:
            binary_data = bytearray(f.read())
        
        py_obj = pdu_to_py_ExecutionUnitRuntimeStatus(binary_data)
        
        with open(output_json_filepath, "w") as f:
            f.write(py_obj.to_json())

    elif command == "write":
        if len(sys.argv) != 4:
            print_usage()
            sys.exit(1)

        input_json_filepath = sys.argv[2]
        output_binary_filepath = sys.argv[3]

        with open(input_json_filepath, "r") as f:
            json_str = f.read()
        
        py_obj = ExecutionUnitRuntimeStatus.from_json(json_str)
        
        binary_data = py_to_pdu_ExecutionUnitRuntimeStatus(py_obj)

        with open(output_binary_filepath, "wb") as f:
            f.write(binary_data)

    else:
        print(f"Unknown command: {command}")
        print_usage()
        sys.exit(1)
