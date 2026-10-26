
import struct
from .pdu_pytype_AckermannStepResponse import AckermannStepResponse
from ..pdu_utils import *
from .. import binary_io

# dependencies for the generated Python class
from ..geometry_msgs.pdu_conv_Transform import *
from ..geometry_msgs.pdu_conv_Twist import *



def pdu_to_py_AckermannStepResponse(binary_data: bytearray) -> AckermannStepResponse:
    py_obj = AckermannStepResponse()
    meta_parser = binary_io.PduMetaDataParser()
    meta = meta_parser.load_pdu_meta(binary_data)
    if meta is None:
        raise ValueError("Invalid PDU binary data: MetaData not found or corrupted")
    binary_read_recursive_AckermannStepResponse(meta, binary_data, py_obj, binary_io.PduMetaData.PDU_META_DATA_SIZE)
    return py_obj


def binary_read_recursive_AckermannStepResponse(meta: binary_io.PduMetaData, binary_data: bytearray, py_obj: AckermannStepResponse, base_off: int):
    # array_type: single 
    # data_type: primitive 
    # member_name: step 
    # type_name: uint64 
    # offset: 0 size: 8 
    # array_len: 1

    
    bin = binary_io.readBinary(binary_data, base_off + 0, 8)
    py_obj.step = binary_io.binTovalue("uint64", bin)
    
    # array_type: single 
    # data_type: primitive 
    # member_name: result_code 
    # type_name: uint32 
    # offset: 8 size: 4 
    # array_len: 1

    
    bin = binary_io.readBinary(binary_data, base_off + 8, 4)
    py_obj.result_code = binary_io.binTovalue("uint32", bin)
    
    # array_type: single 
    # data_type: primitive 
    # member_name: sim_time_usec 
    # type_name: uint64 
    # offset: 16 size: 8 
    # array_len: 1

    
    bin = binary_io.readBinary(binary_data, base_off + 16, 8)
    py_obj.sim_time_usec = binary_io.binTovalue("uint64", bin)
    
    # array_type: single 
    # data_type: struct 
    # member_name: pose 
    # type_name: geometry_msgs/Transform 
    # offset: 24 size: 56 
    # array_len: 1

    tmp_py_obj = Transform()
    binary_read_recursive_Transform(meta, binary_data, tmp_py_obj, base_off + 24)
    py_obj.pose = tmp_py_obj
    
    # array_type: single 
    # data_type: struct 
    # member_name: twist 
    # type_name: geometry_msgs/Twist 
    # offset: 80 size: 48 
    # array_len: 1

    tmp_py_obj = Twist()
    binary_read_recursive_Twist(meta, binary_data, tmp_py_obj, base_off + 80)
    py_obj.twist = tmp_py_obj
    
    return py_obj


def py_to_pdu_AckermannStepResponse(py_obj: AckermannStepResponse) -> bytearray:
    binary_data = bytearray()
    base_allocator = DynamicAllocator(False)
    bw_container = BinaryWriterContainer(binary_io.PduMetaData())
    binary_write_recursive_AckermannStepResponse(0, bw_container, base_allocator, py_obj)

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

def binary_write_recursive_AckermannStepResponse(parent_off: int, bw_container: BinaryWriterContainer, allocator, py_obj: AckermannStepResponse):
    # array_type: single 
    # data_type: primitive 
    # member_name: step 
    # type_name: uint64 
    # offset: 0 size: 8 
    # array_len: 1
    type = "uint64"
    off = 0

    
    bin = binary_io.typeTobin(type, py_obj.step)
    bin = get_binary(type, bin, 8)
    allocator.add(bin, expected_offset=parent_off + off)
    
    # array_type: single 
    # data_type: primitive 
    # member_name: result_code 
    # type_name: uint32 
    # offset: 8 size: 4 
    # array_len: 1
    type = "uint32"
    off = 8

    
    bin = binary_io.typeTobin(type, py_obj.result_code)
    bin = get_binary(type, bin, 4)
    allocator.add(bin, expected_offset=parent_off + off)
    
    # array_type: single 
    # data_type: primitive 
    # member_name: sim_time_usec 
    # type_name: uint64 
    # offset: 16 size: 8 
    # array_len: 1
    type = "uint64"
    off = 16

    
    bin = binary_io.typeTobin(type, py_obj.sim_time_usec)
    bin = get_binary(type, bin, 8)
    allocator.add(bin, expected_offset=parent_off + off)
    
    # array_type: single 
    # data_type: struct 
    # member_name: pose 
    # type_name: geometry_msgs/Transform 
    # offset: 24 size: 56 
    # array_len: 1
    type = "Transform"
    off = 24

    binary_write_recursive_Transform(parent_off + off, bw_container, allocator, py_obj.pose)
    
    # array_type: single 
    # data_type: struct 
    # member_name: twist 
    # type_name: geometry_msgs/Twist 
    # offset: 80 size: 48 
    # array_len: 1
    type = "Twist"
    off = 80

    binary_write_recursive_Twist(parent_off + off, bw_container, allocator, py_obj.twist)
    

if __name__ == "__main__":
    import sys
    import json

    def print_usage():
        print(f"Usage: python -m pdu.python.pdu_conv_AckermannStepResponse <read|write> [args...]")
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
        
        py_obj = pdu_to_py_AckermannStepResponse(binary_data)
        
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
        
        py_obj = AckermannStepResponse.from_json(json_str)
        
        binary_data = py_to_pdu_AckermannStepResponse(py_obj)

        with open(output_binary_filepath, "wb") as f:
            f.write(binary_data)

    else:
        print(f"Unknown command: {command}")
        print_usage()
        sys.exit(1)
