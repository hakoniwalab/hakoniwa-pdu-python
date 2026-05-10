
import struct
from .pdu_pytype_MultiDOFJointState import MultiDOFJointState
from ..pdu_utils import *
from .. import binary_io

# dependencies for the generated Python class
from ..std_msgs.pdu_conv_Header import *
from ..geometry_msgs.pdu_conv_Transform import *
from ..geometry_msgs.pdu_conv_Twist import *
from ..geometry_msgs.pdu_conv_Wrench import *



def pdu_to_py_MultiDOFJointState(binary_data: bytearray) -> MultiDOFJointState:
    py_obj = MultiDOFJointState()
    meta_parser = binary_io.PduMetaDataParser()
    meta = meta_parser.load_pdu_meta(binary_data)
    if meta is None:
        raise ValueError("Invalid PDU binary data: MetaData not found or corrupted")
    binary_read_recursive_MultiDOFJointState(meta, binary_data, py_obj, binary_io.PduMetaData.PDU_META_DATA_SIZE)
    return py_obj


def binary_read_recursive_MultiDOFJointState(meta: binary_io.PduMetaData, binary_data: bytearray, py_obj: MultiDOFJointState, base_off: int):
    # array_type: single 
    # data_type: struct 
    # member_name: header 
    # type_name: std_msgs/Header 
    # offset: 0 size: 136 
    # array_len: 1

    tmp_py_obj = Header()
    binary_read_recursive_Header(meta, binary_data, tmp_py_obj, base_off + 0)
    py_obj.header = tmp_py_obj
    
    # array_type: varray 
    # data_type: primitive 
    # member_name: joint_names 
    # type_name: string 
    # offset: 136 size: 128 
    # array_len: 8

    array_size = binary_io.binTovalue("int32", binary_io.readBinary(binary_data, base_off + 136, 4))
    offset_from_heap = binary_io.binTovalue("int32", binary_io.readBinary(binary_data, base_off + 136 + 4, 4))
    one_elm_size = 128 
    array_value = binary_io.readBinary(binary_data, meta.heap_off + offset_from_heap, one_elm_size * array_size)
    
    py_obj.joint_names = binary_io.binToArrayValues("string", array_value, array_size, one_elm_size)
    
    
    # array_type: varray 
    # data_type: struct 
    # member_name: transforms 
    # type_name: geometry_msgs/Transform 
    # offset: 144 size: 56 
    # array_len: 8

    array_size = binary_io.binTovalue("int32", binary_io.readBinary(binary_data, base_off + 144, 4))
    offset_from_heap = binary_io.binTovalue("int32", binary_io.readBinary(binary_data, base_off + 144 + 4, 4))
    one_elm_size = 56
    i = 0
    array_value = []
    while i < array_size:
        tmp_py_obj = Transform()
        binary_read_recursive_Transform(meta, binary_data, tmp_py_obj, meta.heap_off + offset_from_heap + (i * one_elm_size))
        array_value.append(tmp_py_obj)
        i = i + 1
    py_obj.transforms = array_value    
    
    # array_type: varray 
    # data_type: struct 
    # member_name: twist 
    # type_name: geometry_msgs/Twist 
    # offset: 152 size: 48 
    # array_len: 8

    array_size = binary_io.binTovalue("int32", binary_io.readBinary(binary_data, base_off + 152, 4))
    offset_from_heap = binary_io.binTovalue("int32", binary_io.readBinary(binary_data, base_off + 152 + 4, 4))
    one_elm_size = 48
    i = 0
    array_value = []
    while i < array_size:
        tmp_py_obj = Twist()
        binary_read_recursive_Twist(meta, binary_data, tmp_py_obj, meta.heap_off + offset_from_heap + (i * one_elm_size))
        array_value.append(tmp_py_obj)
        i = i + 1
    py_obj.twist = array_value    
    
    # array_type: varray 
    # data_type: struct 
    # member_name: wrench 
    # type_name: geometry_msgs/Wrench 
    # offset: 160 size: 48 
    # array_len: 8

    array_size = binary_io.binTovalue("int32", binary_io.readBinary(binary_data, base_off + 160, 4))
    offset_from_heap = binary_io.binTovalue("int32", binary_io.readBinary(binary_data, base_off + 160 + 4, 4))
    one_elm_size = 48
    i = 0
    array_value = []
    while i < array_size:
        tmp_py_obj = Wrench()
        binary_read_recursive_Wrench(meta, binary_data, tmp_py_obj, meta.heap_off + offset_from_heap + (i * one_elm_size))
        array_value.append(tmp_py_obj)
        i = i + 1
    py_obj.wrench = array_value    
    
    return py_obj


def py_to_pdu_MultiDOFJointState(py_obj: MultiDOFJointState) -> bytearray:
    binary_data = bytearray()
    base_allocator = DynamicAllocator(False)
    bw_container = BinaryWriterContainer(binary_io.PduMetaData())
    binary_write_recursive_MultiDOFJointState(0, bw_container, base_allocator, py_obj)

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

def binary_write_recursive_MultiDOFJointState(parent_off: int, bw_container: BinaryWriterContainer, allocator, py_obj: MultiDOFJointState):
    # array_type: single 
    # data_type: struct 
    # member_name: header 
    # type_name: std_msgs/Header 
    # offset: 0 size: 136 
    # array_len: 1
    type = "Header"
    off = 0

    binary_write_recursive_Header(parent_off + off, bw_container, allocator, py_obj.header)
    
    # array_type: varray 
    # data_type: primitive 
    # member_name: joint_names 
    # type_name: string 
    # offset: 136 size: 128 
    # array_len: 8
    type = "string"
    off = 136

    offset_from_heap = bw_container.heap_allocator.size()
    array_size = len(py_obj.joint_names)
    a_b = array_size.to_bytes(4, byteorder='little')
    o_b = offset_from_heap.to_bytes(4, byteorder='little')
    allocator.add(a_b + o_b, expected_offset=parent_off + off)
    binary = binary_io.typeTobin_array(type, py_obj.joint_names, 128)
    bw_container.heap_allocator.add(binary)
    
    # array_type: varray 
    # data_type: struct 
    # member_name: transforms 
    # type_name: geometry_msgs/Transform 
    # offset: 144 size: 56 
    # array_len: 8
    type = "Transform"
    off = 144

    offset_from_heap = bw_container.heap_allocator.size()
    array_size = len(py_obj.transforms)
    a_b = array_size.to_bytes(4, byteorder='little')
    o_b = offset_from_heap.to_bytes(4, byteorder='little')
    allocator.add(a_b + o_b, expected_offset=parent_off + off)
    bw_container.heap_allocator.add(bytearray(array_size * 56), expected_offset=offset_from_heap)
    for i, elm in enumerate(py_obj.transforms):
        one_elm_size =  56
        binary_write_recursive_Transform((offset_from_heap + i * one_elm_size), bw_container, bw_container.heap_allocator, elm)
    
    # array_type: varray 
    # data_type: struct 
    # member_name: twist 
    # type_name: geometry_msgs/Twist 
    # offset: 152 size: 48 
    # array_len: 8
    type = "Twist"
    off = 152

    offset_from_heap = bw_container.heap_allocator.size()
    array_size = len(py_obj.twist)
    a_b = array_size.to_bytes(4, byteorder='little')
    o_b = offset_from_heap.to_bytes(4, byteorder='little')
    allocator.add(a_b + o_b, expected_offset=parent_off + off)
    bw_container.heap_allocator.add(bytearray(array_size * 48), expected_offset=offset_from_heap)
    for i, elm in enumerate(py_obj.twist):
        one_elm_size =  48
        binary_write_recursive_Twist((offset_from_heap + i * one_elm_size), bw_container, bw_container.heap_allocator, elm)
    
    # array_type: varray 
    # data_type: struct 
    # member_name: wrench 
    # type_name: geometry_msgs/Wrench 
    # offset: 160 size: 48 
    # array_len: 8
    type = "Wrench"
    off = 160

    offset_from_heap = bw_container.heap_allocator.size()
    array_size = len(py_obj.wrench)
    a_b = array_size.to_bytes(4, byteorder='little')
    o_b = offset_from_heap.to_bytes(4, byteorder='little')
    allocator.add(a_b + o_b, expected_offset=parent_off + off)
    bw_container.heap_allocator.add(bytearray(array_size * 48), expected_offset=offset_from_heap)
    for i, elm in enumerate(py_obj.wrench):
        one_elm_size =  48
        binary_write_recursive_Wrench((offset_from_heap + i * one_elm_size), bw_container, bw_container.heap_allocator, elm)
    

if __name__ == "__main__":
    import sys
    import json

    def print_usage():
        print(f"Usage: python -m pdu.python.pdu_conv_MultiDOFJointState <read|write> [args...]")
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
        
        py_obj = pdu_to_py_MultiDOFJointState(binary_data)
        
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
        
        py_obj = MultiDOFJointState.from_json(json_str)
        
        binary_data = py_to_pdu_MultiDOFJointState(py_obj)

        with open(output_binary_filepath, "wb") as f:
            f.write(binary_data)

    else:
        print(f"Unknown command: {command}")
        print_usage()
        sys.exit(1)
