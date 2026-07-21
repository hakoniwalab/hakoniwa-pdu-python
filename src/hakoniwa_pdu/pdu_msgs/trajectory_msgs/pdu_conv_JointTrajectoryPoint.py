
import struct
from .pdu_pytype_JointTrajectoryPoint import JointTrajectoryPoint
from ..pdu_utils import *
from .. import binary_io

# dependencies for the generated Python class
from ..builtin_interfaces.pdu_conv_Duration import *



def pdu_to_py_JointTrajectoryPoint(binary_data: bytearray) -> JointTrajectoryPoint:
    py_obj = JointTrajectoryPoint()
    meta_parser = binary_io.PduMetaDataParser()
    meta = meta_parser.load_pdu_meta(binary_data)
    if meta is None:
        raise ValueError("Invalid PDU binary data: MetaData not found or corrupted")
    binary_read_recursive_JointTrajectoryPoint(meta, binary_data, py_obj, binary_io.PduMetaData.PDU_META_DATA_SIZE)
    return py_obj


def binary_read_recursive_JointTrajectoryPoint(meta: binary_io.PduMetaData, binary_data: bytearray, py_obj: JointTrajectoryPoint, base_off: int):
    # array_type: varray 
    # data_type: primitive 
    # member_name: positions 
    # type_name: float64 
    # offset: 0 size: 8 
    # array_len: 8

    array_size = binary_io.binTovalue("int32", binary_io.readBinary(binary_data, base_off + 0, 4))
    offset_from_heap = binary_io.binTovalue("int32", binary_io.readBinary(binary_data, base_off + 0 + 4, 4))
    one_elm_size = 8 
    array_value = binary_io.readBinary(binary_data, meta.heap_off + offset_from_heap, one_elm_size * array_size)
    
    py_obj.positions = binary_io.binToArrayValues("float64", array_value)
    
    
    # array_type: varray 
    # data_type: primitive 
    # member_name: velocities 
    # type_name: float64 
    # offset: 8 size: 8 
    # array_len: 8

    array_size = binary_io.binTovalue("int32", binary_io.readBinary(binary_data, base_off + 8, 4))
    offset_from_heap = binary_io.binTovalue("int32", binary_io.readBinary(binary_data, base_off + 8 + 4, 4))
    one_elm_size = 8 
    array_value = binary_io.readBinary(binary_data, meta.heap_off + offset_from_heap, one_elm_size * array_size)
    
    py_obj.velocities = binary_io.binToArrayValues("float64", array_value)
    
    
    # array_type: varray 
    # data_type: primitive 
    # member_name: accelerations 
    # type_name: float64 
    # offset: 16 size: 8 
    # array_len: 8

    array_size = binary_io.binTovalue("int32", binary_io.readBinary(binary_data, base_off + 16, 4))
    offset_from_heap = binary_io.binTovalue("int32", binary_io.readBinary(binary_data, base_off + 16 + 4, 4))
    one_elm_size = 8 
    array_value = binary_io.readBinary(binary_data, meta.heap_off + offset_from_heap, one_elm_size * array_size)
    
    py_obj.accelerations = binary_io.binToArrayValues("float64", array_value)
    
    
    # array_type: varray 
    # data_type: primitive 
    # member_name: effort 
    # type_name: float64 
    # offset: 24 size: 8 
    # array_len: 8

    array_size = binary_io.binTovalue("int32", binary_io.readBinary(binary_data, base_off + 24, 4))
    offset_from_heap = binary_io.binTovalue("int32", binary_io.readBinary(binary_data, base_off + 24 + 4, 4))
    one_elm_size = 8 
    array_value = binary_io.readBinary(binary_data, meta.heap_off + offset_from_heap, one_elm_size * array_size)
    
    py_obj.effort = binary_io.binToArrayValues("float64", array_value)
    
    
    # array_type: single 
    # data_type: struct 
    # member_name: time_from_start 
    # type_name: builtin_interfaces/Duration 
    # offset: 32 size: 8 
    # array_len: 1

    tmp_py_obj = Duration()
    binary_read_recursive_Duration(meta, binary_data, tmp_py_obj, base_off + 32)
    py_obj.time_from_start = tmp_py_obj
    
    return py_obj


def py_to_pdu_JointTrajectoryPoint(py_obj: JointTrajectoryPoint) -> bytearray:
    binary_data = bytearray()
    base_allocator = DynamicAllocator(False)
    bw_container = BinaryWriterContainer(binary_io.PduMetaData())
    binary_write_recursive_JointTrajectoryPoint(0, bw_container, base_allocator, py_obj)

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

def binary_write_recursive_JointTrajectoryPoint(parent_off: int, bw_container: BinaryWriterContainer, allocator, py_obj: JointTrajectoryPoint):
    # array_type: varray 
    # data_type: primitive 
    # member_name: positions 
    # type_name: float64 
    # offset: 0 size: 8 
    # array_len: 8
    type = "float64"
    off = 0

    offset_from_heap = bw_container.heap_allocator.size()
    array_size = len(py_obj.positions)
    a_b = array_size.to_bytes(4, byteorder='little')
    o_b = offset_from_heap.to_bytes(4, byteorder='little')
    allocator.add(a_b + o_b, expected_offset=parent_off + off)
    binary = binary_io.typeTobin_array(type, py_obj.positions, 8)
    bw_container.heap_allocator.add(binary)
    
    # array_type: varray 
    # data_type: primitive 
    # member_name: velocities 
    # type_name: float64 
    # offset: 8 size: 8 
    # array_len: 8
    type = "float64"
    off = 8

    offset_from_heap = bw_container.heap_allocator.size()
    array_size = len(py_obj.velocities)
    a_b = array_size.to_bytes(4, byteorder='little')
    o_b = offset_from_heap.to_bytes(4, byteorder='little')
    allocator.add(a_b + o_b, expected_offset=parent_off + off)
    binary = binary_io.typeTobin_array(type, py_obj.velocities, 8)
    bw_container.heap_allocator.add(binary)
    
    # array_type: varray 
    # data_type: primitive 
    # member_name: accelerations 
    # type_name: float64 
    # offset: 16 size: 8 
    # array_len: 8
    type = "float64"
    off = 16

    offset_from_heap = bw_container.heap_allocator.size()
    array_size = len(py_obj.accelerations)
    a_b = array_size.to_bytes(4, byteorder='little')
    o_b = offset_from_heap.to_bytes(4, byteorder='little')
    allocator.add(a_b + o_b, expected_offset=parent_off + off)
    binary = binary_io.typeTobin_array(type, py_obj.accelerations, 8)
    bw_container.heap_allocator.add(binary)
    
    # array_type: varray 
    # data_type: primitive 
    # member_name: effort 
    # type_name: float64 
    # offset: 24 size: 8 
    # array_len: 8
    type = "float64"
    off = 24

    offset_from_heap = bw_container.heap_allocator.size()
    array_size = len(py_obj.effort)
    a_b = array_size.to_bytes(4, byteorder='little')
    o_b = offset_from_heap.to_bytes(4, byteorder='little')
    allocator.add(a_b + o_b, expected_offset=parent_off + off)
    binary = binary_io.typeTobin_array(type, py_obj.effort, 8)
    bw_container.heap_allocator.add(binary)
    
    # array_type: single 
    # data_type: struct 
    # member_name: time_from_start 
    # type_name: builtin_interfaces/Duration 
    # offset: 32 size: 8 
    # array_len: 1
    type = "Duration"
    off = 32

    binary_write_recursive_Duration(parent_off + off, bw_container, allocator, py_obj.time_from_start)
    

if __name__ == "__main__":
    import sys
    import json

    def print_usage():
        print(f"Usage: python -m pdu.python.pdu_conv_JointTrajectoryPoint <read|write> [args...]")
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
        
        py_obj = pdu_to_py_JointTrajectoryPoint(binary_data)
        
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
        
        py_obj = JointTrajectoryPoint.from_json(json_str)
        
        binary_data = py_to_pdu_JointTrajectoryPoint(py_obj)

        with open(output_binary_filepath, "wb") as f:
            f.write(binary_data)

    else:
        print(f"Unknown command: {command}")
        print_usage()
        sys.exit(1)
