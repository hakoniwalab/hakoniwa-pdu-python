from abc import ABC, abstractmethod

class ICommunicationService(ABC):
    @abstractmethod
    def start_service(self, comm_buffer, uri: str = "") -> bool:
        pass

    @abstractmethod
    def stop_service(self) -> bool:
        pass

    @abstractmethod
    def is_service_enabled(self) -> bool:
        pass

    @abstractmethod
    def send_data(self, robot_name: str, channel_id: int, pdu_data: bytearray) -> bool:
        pass

    @abstractmethod
    def get_server_uri(self) -> str:
        pass
