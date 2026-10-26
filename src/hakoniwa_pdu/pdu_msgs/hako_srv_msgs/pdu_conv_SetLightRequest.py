
import struct
from .pdu_pytype_SetLightRequest import SetLightRequest
from ..pdu_utils import *
from .. import binary_io

# dependencies for the generated Python class



def pdu_to_py_SetLightRequest(binary_data: bytearray) -> SetLightRequest:
    py_obj = SetLightRequest()
    meta_parser = binary_io.PduMetaDataParser()
    meta = meta_parser.load_pdu_meta(binary_data)
    if meta is None:
        raise ValueError("Invalid PDU binary data: MetaData not found or corrupted")
    binary_read_recursive_SetLightRequest(meta, binary_data, py_obj, binary_io.PduMetaData.PDU_META_DATA_SIZE)
    return py_obj


def binary_read_recursive_SetLightRequest(meta: binary_io.PduMetaData, binary_data: bytearray, py_obj: SetLightRequest, base_off: int):
    # array_type: single 
    # data_type: primitive 
    # member_name: source 
    # type_name: string 
    # offset: 0 size: 128 
    # array_len: 1

    
    bin = binary_io.readBinary(binary_data, base_off + 0, 128)
    py_obj.source = binary_io.binTovalue("string", bin)
    
    # array_type: single 
    # data_type: primitive 
    # member_name: mode 
    # type_name: uint8 
    # offset: 128 size: 1 
    # array_len: 1

    
    bin = binary_io.readBinary(binary_data, base_off + 128, 1)
    py_obj.mode = binary_io.binTovalue("uint8", bin)
    
    # array_type: single 
    # data_type: primitive 
    # member_name: luminous_intensity_scale 
    # type_name: float64 
    # offset: 136 size: 8 
    # array_len: 1

    
    bin = binary_io.readBinary(binary_data, base_off + 136, 8)
    py_obj.luminous_intensity_scale = binary_io.binTovalue("float64", bin)
    
    # array_type: single 
    # data_type: primitive 
    # member_name: flashing_on_s 
    # type_name: float64 
    # offset: 144 size: 8 
    # array_len: 1

    
    bin = binary_io.readBinary(binary_data, base_off + 144, 8)
    py_obj.flashing_on_s = binary_io.binTovalue("float64", bin)
    
    # array_type: single 
    # data_type: primitive 
    # member_name: flashing_off_s 
    # type_name: float64 
    # offset: 152 size: 8 
    # array_len: 1

    
    bin = binary_io.readBinary(binary_data, base_off + 152, 8)
    py_obj.flashing_off_s = binary_io.binTovalue("float64", bin)
    
    # array_type: single 
    # data_type: primitive 
    # member_name: transition_s 
    # type_name: float64 
    # offset: 160 size: 8 
    # array_len: 1

    
    bin = binary_io.readBinary(binary_data, base_off + 160, 8)
    py_obj.transition_s = binary_io.binTovalue("float64", bin)
    
    return py_obj


def py_to_pdu_SetLightRequest(py_obj: SetLightRequest) -> bytearray:
    binary_data = bytearray()
    base_allocator = DynamicAllocator(False)
    bw_container = BinaryWriterContainer(binary_io.PduMetaData())
    binary_write_recursive_SetLightRequest(0, bw_container, base_allocator, py_obj)

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

def binary_write_recursive_SetLightRequest(parent_off: int, bw_container: BinaryWriterContainer, allocator, py_obj: SetLightRequest):
    # array_type: single 
    # data_type: primitive 
    # member_name: source 
    # type_name: string 
    # offset: 0 size: 128 
    # array_len: 1
    type = "string"
    off = 0

    
    bin = binary_io.typeTobin(type, py_obj.source)
    bin = get_binary(type, bin, 128)
    allocator.add(bin, expected_offset=parent_off + off)
    
    # array_type: single 
    # data_type: primitive 
    # member_name: mode 
    # type_name: uint8 
    # offset: 128 size: 1 
    # array_len: 1
    type = "uint8"
    off = 128

    
    bin = binary_io.typeTobin(type, py_obj.mode)
    bin = get_binary(type, bin, 1)
    allocator.add(bin, expected_offset=parent_off + off)
    
    # array_type: single 
    # data_type: primitive 
    # member_name: luminous_intensity_scale 
    # type_name: float64 
    # offset: 136 size: 8 
    # array_len: 1
    type = "float64"
    off = 136

    
    bin = binary_io.typeTobin(type, py_obj.luminous_intensity_scale)
    bin = get_binary(type, bin, 8)
    allocator.add(bin, expected_offset=parent_off + off)
    
    # array_type: single 
    # data_type: primitive 
    # member_name: flashing_on_s 
    # type_name: float64 
    # offset: 144 size: 8 
    # array_len: 1
    type = "float64"
    off = 144

    
    bin = binary_io.typeTobin(type, py_obj.flashing_on_s)
    bin = get_binary(type, bin, 8)
    allocator.add(bin, expected_offset=parent_off + off)
    
    # array_type: single 
    # data_type: primitive 
    # member_name: flashing_off_s 
    # type_name: float64 
    # offset: 152 size: 8 
    # array_len: 1
    type = "float64"
    off = 152

    
    bin = binary_io.typeTobin(type, py_obj.flashing_off_s)
    bin = get_binary(type, bin, 8)
    allocator.add(bin, expected_offset=parent_off + off)
    
    # array_type: single 
    # data_type: primitive 
    # member_name: transition_s 
    # type_name: float64 
    # offset: 160 size: 8 
    # array_len: 1
    type = "float64"
    off = 160

    
    bin = binary_io.typeTobin(type, py_obj.transition_s)
    bin = get_binary(type, bin, 8)
    allocator.add(bin, expected_offset=parent_off + off)
    

if __name__ == "__main__":
    import sys
    import json

    def print_usage():
        print(f"Usage: python -m pdu.python.pdu_conv_SetLightRequest <read|write> [args...]")
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
        
        py_obj = pdu_to_py_SetLightRequest(binary_data)
        
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
        
        py_obj = SetLightRequest.from_json(json_str)
        
        binary_data = py_to_pdu_SetLightRequest(py_obj)

        with open(output_binary_filepath, "wb") as f:
            f.write(binary_data)

    else:
        print(f"Unknown command: {command}")
        print_usage()
        sys.exit(1)
