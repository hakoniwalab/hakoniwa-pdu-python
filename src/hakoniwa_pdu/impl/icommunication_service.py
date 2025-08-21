from abc import ABC, abstractmethod
from .pdu_channel_config import PduChannelConfig

class ICommunicationService(ABC):
    @abstractmethod
    def set_channel_config(self, config: PduChannelConfig):
        """Set the PDU channel configuration."""
        pass

    @abstractmethod
    async def start_service(self, comm_buffer, uri: str = "", polling_interval: float = 0.02) -> bool:
        pass

    @abstractmethod
    async def stop_service(self) -> bool:
        pass

    @abstractmethod
    def start_service_nowait(self, comm_buffer, uri: str = "") -> bool:
        pass

    @abstractmethod
    def stop_service_nowait(self) -> bool:
        pass

    @abstractmethod
    def run_nowait(self) -> bool:
        pass


    @abstractmethod
    def is_service_enabled(self) -> bool:
        pass

    @abstractmethod
    async def send_data(self, robot_name: str, channel_id: int, pdu_data: bytearray) -> bool:
        pass

    @abstractmethod
    async def send_binary(self, raw_data: bytearray) -> bool:
        pass

    @abstractmethod
    def register_event_handler(self, handler: callable):
        pass

    @abstractmethod
    async def send_data_nowait(self, robot_name: str, channel_id: int, pdu_data: bytearray) -> bool:
        pass


    @abstractmethod
    def get_server_uri(self) -> str:
        pass
