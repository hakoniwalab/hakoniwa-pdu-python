from .pdu_channel_config import PduChannelConfig
from hako_binary import offset_map
from hako_binary import binary_writer
from hako_binary import binary_reader

class PduConvertor:
    def __init__(self, offset_path: str, pdu_channel_config: PduChannelConfig):
        self.pdu_channel_config = pdu_channel_config
        self.offmap = offset_map.create_offmap(offset_path)

    def create_empty_pdu_json(self, robot_name: str, pdu_name: str) -> dict:
        pdu_size = self.pdu_channel_config.get_pdu_size(robot_name, pdu_name)
        if pdu_size < 0:
            raise ValueError(f"PDU size for {robot_name}/{pdu_name} is not defined.")
        pdu_type = self.pdu_channel_config.get_pdu_type(robot_name, pdu_name)
        if pdu_type is None:
            raise ValueError(f"PDU type for {robot_name}/{pdu_name} is not defined.")
        binary_data = bytearray(pdu_size)
        value = binary_reader.binary_read(self.offmap, pdu_type, binary_data)
        return value

    def convert_json_to_binary(self, robot_name: str, pdu_name: str, json_data: dict) -> bytearray:
        pdu_size = self.pdu_channel_config.get_pdu_size(robot_name, pdu_name)
        if pdu_size < 0:
            raise ValueError(f"PDU size for {robot_name}/{pdu_name} is not defined.")
        pdu_type = self.pdu_channel_config.get_pdu_type(robot_name, pdu_name)
        if pdu_type is None:
            raise ValueError(f"PDU type for {robot_name}/{pdu_name} is not defined.")
        
        binary_data = bytearray(pdu_size)
        binary_writer.binary_write(self.offmap, binary_data, json_data, pdu_type)
        return binary_data
    
    def convert_binary_to_json(self, robot_name: str, pdu_name: str, binary_data: bytearray) -> dict:
        print(f"[DEBUG] Converting binary data for {robot_name}/{pdu_name} of size {len(binary_data)}")
        pdu_type = self.pdu_channel_config.get_pdu_type(robot_name, pdu_name)
        print(f"[DEBUG] PDU type for {robot_name}/{pdu_name}: {pdu_type}")
        if pdu_type is None:
            raise ValueError(f"PDU type for {robot_name}/{pdu_name} is not defined.")
        
        json_data = binary_reader.binary_read(self.offmap, pdu_type, binary_data)
        return json_data
    