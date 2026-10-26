
import struct
from .pdu_pytype_RenderObject import RenderObject
from ..pdu_utils import *
from .. import binary_io

# dependencies for the generated Python class
from ..geometry_msgs.pdu_conv_Pose import *



def pdu_to_py_RenderObject(binary_data: bytearray) -> RenderObject:
    py_obj = RenderObject()
    meta_parser = binary_io.PduMetaDataParser()
    meta = meta_parser.load_pdu_meta(binary_data)
    if meta is None:
        raise ValueError("Invalid PDU binary data: MetaData not found or corrupted")
    binary_read_recursive_RenderObject(meta, binary_data, py_obj, binary_io.PduMetaData.PDU_META_DATA_SIZE)
    return py_obj


def binary_read_recursive_RenderObject(meta: binary_io.PduMetaData, binary_data: bytearray, py_obj: RenderObject, base_off: int):
    # array_type: single 
    # data_type: primitive 
    # member_name: name 
    # type_name: string 
    # offset: 0 size: 128 
    # array_len: 1

    
    bin = binary_io.readBinary(binary_data, base_off + 0, 128)
    py_obj.name = binary_io.binTovalue("string", bin)
    
    # array_type: single 
    # data_type: primitive 
    # member_name: model 
    # type_name: string 
    # offset: 128 size: 128 
    # array_len: 1

    
    bin = binary_io.readBinary(binary_data, base_off + 128, 128)
    py_obj.model = binary_io.binTovalue("string", bin)
    
    # array_type: single 
    # data_type: struct 
    # member_name: pose 
    # type_name: geometry_msgs/Pose 
    # offset: 256 size: 56 
    # array_len: 1

    tmp_py_obj = Pose()
    binary_read_recursive_Pose(meta, binary_data, tmp_py_obj, base_off + 256)
    py_obj.pose = tmp_py_obj
    
    return py_obj


def py_to_pdu_RenderObject(py_obj: RenderObject) -> bytearray:
    binary_data = bytearray()
    base_allocator = DynamicAllocator(False)
    bw_container = BinaryWriterContainer(binary_io.PduMetaData())
    binary_write_recursive_RenderObject(0, bw_container, base_allocator, py_obj)

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

def binary_write_recursive_RenderObject(parent_off: int, bw_container: BinaryWriterContainer, allocator, py_obj: RenderObject):
    # array_type: single 
    # data_type: primitive 
    # member_name: name 
    # type_name: string 
    # offset: 0 size: 128 
    # array_len: 1
    type = "string"
    off = 0

    
    bin = binary_io.typeTobin(type, py_obj.name)
    bin = get_binary(type, bin, 128)
    allocator.add(bin, expected_offset=parent_off + off)
    
    # array_type: single 
    # data_type: primitive 
    # member_name: model 
    # type_name: string 
    # offset: 128 size: 128 
    # array_len: 1
    type = "string"
    off = 128

    
    bin = binary_io.typeTobin(type, py_obj.model)
    bin = get_binary(type, bin, 128)
    allocator.add(bin, expected_offset=parent_off + off)
    
    # array_type: single 
    # data_type: struct 
    # member_name: pose 
    # type_name: geometry_msgs/Pose 
    # offset: 256 size: 56 
    # array_len: 1
    type = "Pose"
    off = 256

    binary_write_recursive_Pose(parent_off + off, bw_container, allocator, py_obj.pose)
    

if __name__ == "__main__":
    import sys
    import json

    def print_usage():
        print(f"Usage: python -m pdu.python.pdu_conv_RenderObject <read|write> [args...]")
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
        
        py_obj = pdu_to_py_RenderObject(binary_data)
        
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
        
        py_obj = RenderObject.from_json(json_str)
        
        binary_data = py_to_pdu_RenderObject(py_obj)

        with open(output_binary_filepath, "wb") as f:
            f.write(binary_data)

    else:
        print(f"Unknown command: {command}")
        print_usage()
        sys.exit(1)
