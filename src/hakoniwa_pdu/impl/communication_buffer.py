import threading
import logging
from typing import Tuple, Optional
from .pdu_channel_config import PduChannelConfig
from .data_packet import DataPacket

logger = logging.getLogger(__name__)

class CommunicationBuffer:
    def __init__(self, pdu_channel_config: PduChannelConfig):
        self.pdu_buffer = {}  # Dict[Tuple[str, str], bytearray]
        self.lock = threading.Lock()
        self.pdu_channel_config = pdu_channel_config

    def set_buffer(self, robot_name: str, pdu_name: str, data: bytearray):
        #logger.debug(f"set_buffer: key=({robot_name}, {pdu_name})")
        with self.lock:
            self.pdu_buffer[(robot_name, pdu_name)] = data

    def get_buffer(self, robot_name: str, pdu_name: str) -> bytearray:
        with self.lock:
            return self.pdu_buffer.pop((robot_name, pdu_name), bytearray())

    def peek_buffer(self, robot_name: str, pdu_name: str) -> bytearray:
        with self.lock:
            return self.pdu_buffer.get((robot_name, pdu_name), bytearray())

    def contains_buffer(self, robot_name: str, pdu_name: str) -> bool:
        #logger.debug(f"contains_buffer: key=({robot_name}, {pdu_name})")
        with self.lock:
            return (robot_name, pdu_name) in self.pdu_buffer

    def clear(self):
        with self.lock:
            self.pdu_buffer.clear()

    def get_pdu_name(self, robot_name: str, channel_id: int) -> Optional[str]:
        return self.pdu_channel_config.get_pdu_name(robot_name, channel_id)

    def get_pdu_size(self, robot_name: str, pdu_name: str) -> int:
        return self.pdu_channel_config.get_pdu_size(robot_name, pdu_name)

    def get_pdu_channel_id(self, robot_name: str, pdu_name: str) -> int:
        return self.pdu_channel_config.get_pdu_channel_id(robot_name, pdu_name)

    def put_packet(self, packet: DataPacket):
        robot_name = packet.get_robot_name()
        channel_id = packet.get_channel_id()
        pdu_name = self.get_pdu_name(robot_name, channel_id)
        if pdu_name is None:
            logger.warning(f"Unknown PDU for {robot_name}:{channel_id}")
            return
        self.set_buffer(robot_name, pdu_name, packet.get_pdu_data())

    def put_packet_direct(self, robot_name: str, channel_id: int, pdu_data: bytearray):
        pdu_name = self.get_pdu_name(robot_name, channel_id)
        if pdu_name is None:
            logger.warning(f"Unknown PDU for {robot_name}:{channel_id}")
            return
        self.set_buffer(robot_name, pdu_name, pdu_data)

    def put_rpc_packet(self, service_name: str, client_name: str, pdu_data: bytearray):
        #logger.debug(f"put_rpc_packet: service={service_name}, client={client_name}")
        self.set_buffer(service_name, client_name, pdu_data)