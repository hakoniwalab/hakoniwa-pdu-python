
import struct
from .pdu_pytype_NavSatFix import NavSatFix
from ..pdu_utils import *
from .. import binary_io

# dependencies for the generated Python class
from ..std_msgs.pdu_conv_Header import *
from ..sensor_msgs.pdu_conv_NavSatStatus import *



def pdu_to_py_NavSatFix(binary_data: bytearray) -> NavSatFix:
    py_obj = NavSatFix()
    meta_parser = binary_io.PduMetaDataParser()
    meta = meta_parser.load_pdu_meta(binary_data)
    if meta is None:
        raise ValueError("Invalid PDU binary data: MetaData not found or corrupted")
    binary_read_recursive_NavSatFix(meta, binary_data, py_obj, binary_io.PduMetaData.PDU_META_DATA_SIZE)
    return py_obj


def binary_read_recursive_NavSatFix(meta: binary_io.PduMetaData, binary_data: bytearray, py_obj: NavSatFix, base_off: int):
    # array_type: single 
    # data_type: struct 
    # member_name: header 
    # type_name: std_msgs/Header 
    # offset: 0 size: 136 
    # array_len: 1

    tmp_py_obj = Header()
    binary_read_recursive_Header(meta, binary_data, tmp_py_obj, base_off + 0)
    py_obj.header = tmp_py_obj
    
    # array_type: single 
    # data_type: struct 
    # member_name: status 
    # type_name: NavSatStatus 
    # offset: 136 size: 4 
    # array_len: 1

    tmp_py_obj = NavSatStatus()
    binary_read_recursive_NavSatStatus(meta, binary_data, tmp_py_obj, base_off + 136)
    py_obj.status = tmp_py_obj
    
    # array_type: single 
    # data_type: primitive 
    # member_name: latitude 
    # type_name: float64 
    # offset: 144 size: 8 
    # array_len: 1

    
    bin = binary_io.readBinary(binary_data, base_off + 144, 8)
    py_obj.latitude = binary_io.binTovalue("float64", bin)
    
    # array_type: single 
    # data_type: primitive 
    # member_name: longitude 
    # type_name: float64 
    # offset: 152 size: 8 
    # array_len: 1

    
    bin = binary_io.readBinary(binary_data, base_off + 152, 8)
    py_obj.longitude = binary_io.binTovalue("float64", bin)
    
    # array_type: single 
    # data_type: primitive 
    # member_name: altitude 
    # type_name: float64 
    # offset: 160 size: 8 
    # array_len: 1

    
    bin = binary_io.readBinary(binary_data, base_off + 160, 8)
    py_obj.altitude = binary_io.binTovalue("float64", bin)
    
    # array_type: array 
    # data_type: primitive 
    # member_name: position_covariance 
    # type_name: float64 
    # offset: 168 size: 72 
    # array_len: 9

    
    array_value = binary_io.readBinary(binary_data, base_off + 168, 72)
    
    py_obj.position_covariance = binary_io.binToArrayValues("float64", array_value)
    
    
    # array_type: single 
    # data_type: primitive 
    # member_name: position_covariance_type 
    # type_name: uint8 
    # offset: 240 size: 1 
    # array_len: 1

    
    bin = binary_io.readBinary(binary_data, base_off + 240, 1)
    py_obj.position_covariance_type = binary_io.binTovalue("uint8", bin)
    
    return py_obj


def py_to_pdu_NavSatFix(py_obj: NavSatFix) -> bytearray:
    binary_data = bytearray()
    base_allocator = DynamicAllocator(False)
    bw_container = BinaryWriterContainer(binary_io.PduMetaData())
    binary_write_recursive_NavSatFix(0, bw_container, base_allocator, py_obj)

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

def binary_write_recursive_NavSatFix(parent_off: int, bw_container: BinaryWriterContainer, allocator, py_obj: NavSatFix):
    # array_type: single 
    # data_type: struct 
    # member_name: header 
    # type_name: std_msgs/Header 
    # offset: 0 size: 136 
    # array_len: 1
    type = "Header"
    off = 0

    binary_write_recursive_Header(parent_off + off, bw_container, allocator, py_obj.header)
    
    # array_type: single 
    # data_type: struct 
    # member_name: status 
    # type_name: NavSatStatus 
    # offset: 136 size: 4 
    # array_len: 1
    type = "NavSatStatus"
    off = 136

    binary_write_recursive_NavSatStatus(parent_off + off, bw_container, allocator, py_obj.status)
    
    # array_type: single 
    # data_type: primitive 
    # member_name: latitude 
    # type_name: float64 
    # offset: 144 size: 8 
    # array_len: 1
    type = "float64"
    off = 144

    
    bin = binary_io.typeTobin(type, py_obj.latitude)
    bin = get_binary(type, bin, 8)
    allocator.add(bin, expected_offset=parent_off + off)
    
    # array_type: single 
    # data_type: primitive 
    # member_name: longitude 
    # type_name: float64 
    # offset: 152 size: 8 
    # array_len: 1
    type = "float64"
    off = 152

    
    bin = binary_io.typeTobin(type, py_obj.longitude)
    bin = get_binary(type, bin, 8)
    allocator.add(bin, expected_offset=parent_off + off)
    
    # array_type: single 
    # data_type: primitive 
    # member_name: altitude 
    # type_name: float64 
    # offset: 160 size: 8 
    # array_len: 1
    type = "float64"
    off = 160

    
    bin = binary_io.typeTobin(type, py_obj.altitude)
    bin = get_binary(type, bin, 8)
    allocator.add(bin, expected_offset=parent_off + off)
    
    # array_type: array 
    # data_type: primitive 
    # member_name: position_covariance 
    # type_name: float64 
    # offset: 168 size: 72 
    # array_len: 9
    type = "float64"
    off = 168

    
    one_elm_size = int(8.0)
    binary = binary_io.typeTobin_array(type, py_obj.position_covariance, one_elm_size)
    allocator.add(binary, expected_offset=(parent_off + off))
    
    # array_type: single 
    # data_type: primitive 
    # member_name: position_covariance_type 
    # type_name: uint8 
    # offset: 240 size: 1 
    # array_len: 1
    type = "uint8"
    off = 240

    
    bin = binary_io.typeTobin(type, py_obj.position_covariance_type)
    bin = get_binary(type, bin, 1)
    allocator.add(bin, expected_offset=parent_off + off)
    

if __name__ == "__main__":
    import sys
    import json

    def print_usage():
        print(f"Usage: python -m pdu.python.pdu_conv_NavSatFix <read|write> [args...]")
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
        
        py_obj = pdu_to_py_NavSatFix(binary_data)
        
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
        
        py_obj = NavSatFix.from_json(json_str)
        
        binary_data = py_to_pdu_NavSatFix(py_obj)

        with open(output_binary_filepath, "wb") as f:
            f.write(binary_data)

    else:
        print(f"Unknown command: {command}")
        print_usage()
        sys.exit(1)
