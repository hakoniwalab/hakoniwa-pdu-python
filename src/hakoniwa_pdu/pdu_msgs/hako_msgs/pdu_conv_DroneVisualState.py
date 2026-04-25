
import struct
from .pdu_pytype_DroneVisualState import DroneVisualState
from ..pdu_utils import *
from .. import binary_io

# dependencies for the generated Python class



def pdu_to_py_DroneVisualState(binary_data: bytearray) -> DroneVisualState:
    py_obj = DroneVisualState()
    meta_parser = binary_io.PduMetaDataParser()
    meta = meta_parser.load_pdu_meta(binary_data)
    if meta is None:
        raise ValueError("Invalid PDU binary data: MetaData not found or corrupted")
    binary_read_recursive_DroneVisualState(meta, binary_data, py_obj, binary_io.PduMetaData.PDU_META_DATA_SIZE)
    return py_obj


def binary_read_recursive_DroneVisualState(meta: binary_io.PduMetaData, binary_data: bytearray, py_obj: DroneVisualState, base_off: int):
    # array_type: single 
    # data_type: primitive 
    # member_name: x 
    # type_name: float32 
    # offset: 0 size: 4 
    # array_len: 1

    
    bin = binary_io.readBinary(binary_data, base_off + 0, 4)
    py_obj.x = binary_io.binTovalue("float32", bin)
    
    # array_type: single 
    # data_type: primitive 
    # member_name: y 
    # type_name: float32 
    # offset: 4 size: 4 
    # array_len: 1

    
    bin = binary_io.readBinary(binary_data, base_off + 4, 4)
    py_obj.y = binary_io.binTovalue("float32", bin)
    
    # array_type: single 
    # data_type: primitive 
    # member_name: z 
    # type_name: float32 
    # offset: 8 size: 4 
    # array_len: 1

    
    bin = binary_io.readBinary(binary_data, base_off + 8, 4)
    py_obj.z = binary_io.binTovalue("float32", bin)
    
    # array_type: single 
    # data_type: primitive 
    # member_name: roll 
    # type_name: float32 
    # offset: 12 size: 4 
    # array_len: 1

    
    bin = binary_io.readBinary(binary_data, base_off + 12, 4)
    py_obj.roll = binary_io.binTovalue("float32", bin)
    
    # array_type: single 
    # data_type: primitive 
    # member_name: pitch 
    # type_name: float32 
    # offset: 16 size: 4 
    # array_len: 1

    
    bin = binary_io.readBinary(binary_data, base_off + 16, 4)
    py_obj.pitch = binary_io.binTovalue("float32", bin)
    
    # array_type: single 
    # data_type: primitive 
    # member_name: yaw 
    # type_name: float32 
    # offset: 20 size: 4 
    # array_len: 1

    
    bin = binary_io.readBinary(binary_data, base_off + 20, 4)
    py_obj.yaw = binary_io.binTovalue("float32", bin)
    
    # array_type: varray 
    # data_type: primitive 
    # member_name: pwm_duty 
    # type_name: float32 
    # offset: 24 size: 4 
    # array_len: 8

    array_size = binary_io.binTovalue("int32", binary_io.readBinary(binary_data, base_off + 24, 4))
    offset_from_heap = binary_io.binTovalue("int32", binary_io.readBinary(binary_data, base_off + 24 + 4, 4))
    one_elm_size = 4 
    array_value = binary_io.readBinary(binary_data, meta.heap_off + offset_from_heap, one_elm_size * array_size)
    
    py_obj.pwm_duty = binary_io.binToArrayValues("float32", array_value)
    
    
    return py_obj


def py_to_pdu_DroneVisualState(py_obj: DroneVisualState) -> bytearray:
    binary_data = bytearray()
    base_allocator = DynamicAllocator(False)
    bw_container = BinaryWriterContainer(binary_io.PduMetaData())
    binary_write_recursive_DroneVisualState(0, bw_container, base_allocator, py_obj)

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

def binary_write_recursive_DroneVisualState(parent_off: int, bw_container: BinaryWriterContainer, allocator, py_obj: DroneVisualState):
    # array_type: single 
    # data_type: primitive 
    # member_name: x 
    # type_name: float32 
    # offset: 0 size: 4 
    # array_len: 1
    type = "float32"
    off = 0

    
    bin = binary_io.typeTobin(type, py_obj.x)
    bin = get_binary(type, bin, 4)
    allocator.add(bin, expected_offset=parent_off + off)
    
    # array_type: single 
    # data_type: primitive 
    # member_name: y 
    # type_name: float32 
    # offset: 4 size: 4 
    # array_len: 1
    type = "float32"
    off = 4

    
    bin = binary_io.typeTobin(type, py_obj.y)
    bin = get_binary(type, bin, 4)
    allocator.add(bin, expected_offset=parent_off + off)
    
    # array_type: single 
    # data_type: primitive 
    # member_name: z 
    # type_name: float32 
    # offset: 8 size: 4 
    # array_len: 1
    type = "float32"
    off = 8

    
    bin = binary_io.typeTobin(type, py_obj.z)
    bin = get_binary(type, bin, 4)
    allocator.add(bin, expected_offset=parent_off + off)
    
    # array_type: single 
    # data_type: primitive 
    # member_name: roll 
    # type_name: float32 
    # offset: 12 size: 4 
    # array_len: 1
    type = "float32"
    off = 12

    
    bin = binary_io.typeTobin(type, py_obj.roll)
    bin = get_binary(type, bin, 4)
    allocator.add(bin, expected_offset=parent_off + off)
    
    # array_type: single 
    # data_type: primitive 
    # member_name: pitch 
    # type_name: float32 
    # offset: 16 size: 4 
    # array_len: 1
    type = "float32"
    off = 16

    
    bin = binary_io.typeTobin(type, py_obj.pitch)
    bin = get_binary(type, bin, 4)
    allocator.add(bin, expected_offset=parent_off + off)
    
    # array_type: single 
    # data_type: primitive 
    # member_name: yaw 
    # type_name: float32 
    # offset: 20 size: 4 
    # array_len: 1
    type = "float32"
    off = 20

    
    bin = binary_io.typeTobin(type, py_obj.yaw)
    bin = get_binary(type, bin, 4)
    allocator.add(bin, expected_offset=parent_off + off)
    
    # array_type: varray 
    # data_type: primitive 
    # member_name: pwm_duty 
    # type_name: float32 
    # offset: 24 size: 4 
    # array_len: 8
    type = "float32"
    off = 24

    offset_from_heap = bw_container.heap_allocator.size()
    array_size = len(py_obj.pwm_duty)
    a_b = array_size.to_bytes(4, byteorder='little')
    o_b = offset_from_heap.to_bytes(4, byteorder='little')
    allocator.add(a_b + o_b, expected_offset=parent_off + off)
    binary = binary_io.typeTobin_array(type, py_obj.pwm_duty, 4)
    bw_container.heap_allocator.add(binary)
    

if __name__ == "__main__":
    import sys
    import json

    def print_usage():
        print(f"Usage: python -m pdu.python.pdu_conv_DroneVisualState <read|write> [args...]")
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
        
        py_obj = pdu_to_py_DroneVisualState(binary_data)
        
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
        
        py_obj = DroneVisualState.from_json(json_str)
        
        binary_data = py_to_pdu_DroneVisualState(py_obj)

        with open(output_binary_filepath, "wb") as f:
            f.write(binary_data)

    else:
        print(f"Unknown command: {command}")
        print_usage()
        sys.exit(1)
