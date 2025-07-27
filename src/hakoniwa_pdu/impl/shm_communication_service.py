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
        if not self.config:
            print("[ERROR] Channel configuration is not set")
            return False
        self.comm_buffer = comm_buffer
        self.polling_interval = polling_interval
        self._loop = asyncio.get_event_loop()

        try:
            self._receive_task = asyncio.create_task(self._receive_loop())
            self.service_enabled = True
            print("[INFO] Shm receive loop started")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to start Shm receive loop: {e}")
            self.service_enabled = False
            return False


    async def stop_service(self) -> bool:
        self.service_enabled = False

        if self._receive_task:
            self._receive_task.cancel()
            try:
                await self._receive_task
            except asyncio.CancelledError:
                pass

        self._receive_task = None
        return True

    def is_service_enabled(self) -> bool:
        return self.service_enabled

    def get_server_uri(self) -> str:
        return ""

    async def send_data(self, robot_name: str, channel_id: int, pdu_data: bytearray) -> bool:
        ret : bool = hakopy.pdu_write(robot_name, channel_id, pdu_data, len(pdu_data))
        if not ret:
            print(f"[ERROR] Failed to send data for {robot_name}:{channel_id}")
            return False
        return True

    async def _receive_loop(self):
        if not self.config:
            print("[ERROR] Channel configuration is not set")
            return
        shm_pdu_readers = self.config.get_shm_pdu_readers()
        try:
            # Main loop to read PDUs from shared memory
            # read PDU data from shared memory
            while self.service_enabled:
                for reader in shm_pdu_readers:
                    data : bytearray = hakopy.pdu_read(reader.robot_name, reader.channel_id, reader.pdu_size)
                    if data:
                        packet = DataPacket(reader.robot_name, reader.channel_id, data)
                        self.comm_buffer.add_packet(packet)
                        print(f"[INFO] Received data for {reader.robot_name}:{reader.channel_id}")
                # sleep 20msec
                await asyncio.sleep(self.polling_interval)
        except asyncio.CancelledError:
            print("[INFO] Receive loop cancelled")
        except Exception as e:
            print(f"[ERROR] Receive loop failed: {e}")