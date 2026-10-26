
import struct
from .pdu_pytype_ContactEvent import ContactEvent
from ..pdu_utils import *
from .. import binary_io

# dependencies for the generated Python class
from ..builtin_interfaces.pdu_conv_Time import *
from ..geometry_msgs.pdu_conv_Point import *



def pdu_to_py_ContactEvent(binary_data: bytearray) -> ContactEvent:
    py_obj = ContactEvent()
    meta_parser = binary_io.PduMetaDataParser()
    meta = meta_parser.load_pdu_meta(binary_data)
    if meta is None:
        raise ValueError("Invalid PDU binary data: MetaData not found or corrupted")
    binary_read_recursive_ContactEvent(meta, binary_data, py_obj, binary_io.PduMetaData.PDU_META_DATA_SIZE)
    return py_obj


def binary_read_recursive_ContactEvent(meta: binary_io.PduMetaData, binary_data: bytearray, py_obj: ContactEvent, base_off: int):
    # array_type: single 
    # data_type: struct 
    # member_name: stamp 
    # type_name: builtin_interfaces/Time 
    # offset: 0 size: 8 
    # array_len: 1

    tmp_py_obj = Time()
    binary_read_recursive_Time(meta, binary_data, tmp_py_obj, base_off + 0)
    py_obj.stamp = tmp_py_obj
    
    # array_type: single 
    # data_type: primitive 
    # member_name: self_name 
    # type_name: string 
    # offset: 8 size: 128 
    # array_len: 1

    
    bin = binary_io.readBinary(binary_data, base_off + 8, 128)
    py_obj.self_name = binary_io.binTovalue("string", bin)
    
    # array_type: single 
    # data_type: primitive 
    # member_name: other_name 
    # type_name: string 
    # offset: 136 size: 128 
    # array_len: 1

    
    bin = binary_io.readBinary(binary_data, base_off + 136, 128)
    py_obj.other_name = binary_io.binTovalue("string", bin)
    
    # array_type: single 
    # data_type: primitive 
    # member_name: other_kind 
    # type_name: string 
    # offset: 264 size: 128 
    # array_len: 1

    
    bin = binary_io.readBinary(binary_data, base_off + 264, 128)
    py_obj.other_kind = binary_io.binTovalue("string", bin)
    
    # array_type: single 
    # data_type: struct 
    # member_name: position 
    # type_name: geometry_msgs/Point 
    # offset: 392 size: 24 
    # array_len: 1

    tmp_py_obj = Point()
    binary_read_recursive_Point(meta, binary_data, tmp_py_obj, base_off + 392)
    py_obj.position = tmp_py_obj
    
    # array_type: single 
    # data_type: primitive 
    # member_name: relative_speed 
    # type_name: float64 
    # offset: 416 size: 8 
    # array_len: 1

    
    bin = binary_io.readBinary(binary_data, base_off + 416, 8)
    py_obj.relative_speed = binary_io.binTovalue("float64", bin)
    
    # array_type: single 
    # data_type: primitive 
    # member_name: started 
    # type_name: bool 
    # offset: 424 size: 4 
    # array_len: 1

    
    bin = binary_io.readBinary(binary_data, base_off + 424, 4)
    py_obj.started = binary_io.binTovalue("bool", bin)
    
    return py_obj


def py_to_pdu_ContactEvent(py_obj: ContactEvent) -> bytearray:
    binary_data = bytearray()
    base_allocator = DynamicAllocator(False)
    bw_container = BinaryWriterContainer(binary_io.PduMetaData())
    binary_write_recursive_ContactEvent(0, bw_container, base_allocator, py_obj)

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

def binary_write_recursive_ContactEvent(parent_off: int, bw_container: BinaryWriterContainer, allocator, py_obj: ContactEvent):
    # array_type: single 
    # data_type: struct 
    # member_name: stamp 
    # type_name: builtin_interfaces/Time 
    # offset: 0 size: 8 
    # array_len: 1
    type = "Time"
    off = 0

    binary_write_recursive_Time(parent_off + off, bw_container, allocator, py_obj.stamp)
    
    # array_type: single 
    # data_type: primitive 
    # member_name: self_name 
    # type_name: string 
    # offset: 8 size: 128 
    # array_len: 1
    type = "string"
    off = 8

    
    bin = binary_io.typeTobin(type, py_obj.self_name)
    bin = get_binary(type, bin, 128)
    allocator.add(bin, expected_offset=parent_off + off)
    
    # array_type: single 
    # data_type: primitive 
    # member_name: other_name 
    # type_name: string 
    # offset: 136 size: 128 
    # array_len: 1
    type = "string"
    off = 136

    
    bin = binary_io.typeTobin(type, py_obj.other_name)
    bin = get_binary(type, bin, 128)
    allocator.add(bin, expected_offset=parent_off + off)
    
    # array_type: single 
    # data_type: primitive 
    # member_name: other_kind 
    # type_name: string 
    # offset: 264 size: 128 
    # array_len: 1
    type = "string"
    off = 264

    
    bin = binary_io.typeTobin(type, py_obj.other_kind)
    bin = get_binary(type, bin, 128)
    allocator.add(bin, expected_offset=parent_off + off)
    
    # array_type: single 
    # data_type: struct 
    # member_name: position 
    # type_name: geometry_msgs/Point 
    # offset: 392 size: 24 
    # array_len: 1
    type = "Point"
    off = 392

    binary_write_recursive_Point(parent_off + off, bw_container, allocator, py_obj.position)
    
    # array_type: single 
    # data_type: primitive 
    # member_name: relative_speed 
    # type_name: float64 
    # offset: 416 size: 8 
    # array_len: 1
    type = "float64"
    off = 416

    
    bin = binary_io.typeTobin(type, py_obj.relative_speed)
    bin = get_binary(type, bin, 8)
    allocator.add(bin, expected_offset=parent_off + off)
    
    # array_type: single 
    # data_type: primitive 
    # member_name: started 
    # type_name: bool 
    # offset: 424 size: 4 
    # array_len: 1
    type = "bool"
    off = 424

    
    bin = binary_io.typeTobin(type, py_obj.started)
    bin = get_binary(type, bin, 4)
    allocator.add(bin, expected_offset=parent_off + off)
    

if __name__ == "__main__":
    import sys
    import json

    def print_usage():
        print(f"Usage: python -m pdu.python.pdu_conv_ContactEvent <read|write> [args...]")
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
        
        py_obj = pdu_to_py_ContactEvent(binary_data)
        
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
        
        py_obj = ContactEvent.from_json(json_str)
        
        binary_data = py_to_pdu_ContactEvent(py_obj)

        with open(output_binary_filepath, "wb") as f:
            f.write(binary_data)

    else:
        print(f"Unknown command: {command}")
        print_usage()
        sys.exit(1)
