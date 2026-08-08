
import struct
from .pdu_pytype_FibonacciActionFeedback import FibonacciActionFeedback
from ..pdu_utils import *
from .. import binary_io

# dependencies for the generated Python class
from ..hako_action_msgs.pdu_conv_ActionFeedbackHeader import *
from ..sample_action_msgs.pdu_conv_FibonacciFeedback import *



def pdu_to_py_FibonacciActionFeedback(binary_data: bytearray) -> FibonacciActionFeedback:
    py_obj = FibonacciActionFeedback()
    meta_parser = binary_io.PduMetaDataParser()
    meta = meta_parser.load_pdu_meta(binary_data)
    if meta is None:
        raise ValueError("Invalid PDU binary data: MetaData not found or corrupted")
    binary_read_recursive_FibonacciActionFeedback(meta, binary_data, py_obj, binary_io.PduMetaData.PDU_META_DATA_SIZE)
    return py_obj


def binary_read_recursive_FibonacciActionFeedback(meta: binary_io.PduMetaData, binary_data: bytearray, py_obj: FibonacciActionFeedback, base_off: int):
    # array_type: single 
    # data_type: struct 
    # member_name: header 
    # type_name: hako_action_msgs/ActionFeedbackHeader 
    # offset: 0 size: 24 
    # array_len: 1

    tmp_py_obj = ActionFeedbackHeader()
    binary_read_recursive_ActionFeedbackHeader(meta, binary_data, tmp_py_obj, base_off + 0)
    py_obj.header = tmp_py_obj
    
    # array_type: single 
    # data_type: struct 
    # member_name: body 
    # type_name: FibonacciFeedback 
    # offset: 24 size: 8 
    # array_len: 1

    tmp_py_obj = FibonacciFeedback()
    binary_read_recursive_FibonacciFeedback(meta, binary_data, tmp_py_obj, base_off + 24)
    py_obj.body = tmp_py_obj
    
    return py_obj


def py_to_pdu_FibonacciActionFeedback(py_obj: FibonacciActionFeedback) -> bytearray:
    binary_data = bytearray()
    base_allocator = DynamicAllocator(False)
    bw_container = BinaryWriterContainer(binary_io.PduMetaData())
    binary_write_recursive_FibonacciActionFeedback(0, bw_container, base_allocator, py_obj)

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

def binary_write_recursive_FibonacciActionFeedback(parent_off: int, bw_container: BinaryWriterContainer, allocator, py_obj: FibonacciActionFeedback):
    # array_type: single 
    # data_type: struct 
    # member_name: header 
    # type_name: hako_action_msgs/ActionFeedbackHeader 
    # offset: 0 size: 24 
    # array_len: 1
    type = "ActionFeedbackHeader"
    off = 0

    binary_write_recursive_ActionFeedbackHeader(parent_off + off, bw_container, allocator, py_obj.header)
    
    # array_type: single 
    # data_type: struct 
    # member_name: body 
    # type_name: FibonacciFeedback 
    # offset: 24 size: 8 
    # array_len: 1
    type = "FibonacciFeedback"
    off = 24

    binary_write_recursive_FibonacciFeedback(parent_off + off, bw_container, allocator, py_obj.body)
    

if __name__ == "__main__":
    import sys
    import json

    def print_usage():
        print(f"Usage: python -m pdu.python.pdu_conv_FibonacciActionFeedback <read|write> [args...]")
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
        
        py_obj = pdu_to_py_FibonacciActionFeedback(binary_data)
        
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
        
        py_obj = FibonacciActionFeedback.from_json(json_str)
        
        binary_data = py_to_pdu_FibonacciActionFeedback(py_obj)

        with open(output_binary_filepath, "wb") as f:
            f.write(binary_data)

    else:
        print(f"Unknown command: {command}")
        print_usage()
        sys.exit(1)
