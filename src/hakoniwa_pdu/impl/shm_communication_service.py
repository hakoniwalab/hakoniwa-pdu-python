import asyncio
import hakopy
from typing import Optional
from .data_packet import DataPacket
from .communication_buffer import CommunicationBuffer
from .icommunication_service import ICommunicationService
from .pdu_channel_config import PduChannelConfig

class ShmCommunicationService(ICommunicationService):
    def __init__(self):
        self.service_enabled: bool = False
        self.comm_buffer: Optional[CommunicationBuffer] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._receive_task: Optional[asyncio.Task] = None
        self.config = None

    def set_channel_config(self, config: PduChannelConfig):
        """Set the PDU channel configuration."""
        self.config = config

    async def start_service(self, comm_buffer: CommunicationBuffer, uri: str = "", polling_interval: float = 0.02) -> bool:
        return False  # Not implemented for SHM
    async def stop_service(self) -> bool:
        return False  # Not implemented for SHM


    def start_service_nowait(self, comm_buffer: CommunicationBuffer, uri: str = "") -> bool:
        self.comm_buffer = comm_buffer
        self.service_enabled = True
        return True
    def stop_service_nowait(self) -> bool:
        self.service_enabled = False
        return True

    def is_service_enabled(self) -> bool:
        return self.service_enabled

    def get_server_uri(self) -> str:
        return ""

    async def send_data(self, robot_name: str, channel_id: int, pdu_data: bytearray) -> bool:
        return False  # Not implemented for SHM

    def send_data_nowait(self, robot_name: str, channel_id: int, pdu_data: bytearray) -> bool:
        ret : bool = hakopy.pdu_write(robot_name, channel_id, pdu_data, len(pdu_data))
        if not ret:
            print(f"[ERROR] Failed to send data for {robot_name}:{channel_id}")
            return False
        return True

    def run_nowait(self) -> bool:
        if not self.config:
            print("[ERROR] Channel configuration is not set")
            return False
        unique_list = list(set(self.config.get_shm_pdu_readers()) | set(self.config.get_shm_pdu_writers()))
        try:
            # read PDU data from shared memory
            for reader in unique_list:
                data : bytearray = hakopy.pdu_read(reader.robot_name, reader.channel_id, reader.pdu_size)
                if data:
                    packet = DataPacket(reader.robot_name, reader.channel_id, data)
                    self.comm_buffer.put_packet(packet)
                    #print(f"[INFO] Received data for {reader.robot_name}:{reader.channel_id}")
        except Exception as e:
            print(f"[ERROR] Receive loop failed: {e}")
            return False
        return True

    async def send_binary(self, raw_data: bytearray) -> bool:
        pass # not supported

    def register_event_handler(self, handler: callable):
        """Register an event handler for a specific event type."""
        pass