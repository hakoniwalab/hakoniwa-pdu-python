from typing import Optional
from impl.communication_buffer import CommunicationBuffer
from impl.icommunication_service import ICommunicationService
from impl.data_packet import DataPacket
from impl.pdu_channel_config import PduChannelConfig  # ← 追加

class PduManager:
    def __init__(self):
        self.comm_buffer: Optional[CommunicationBuffer] = None
        self.comm_service: Optional[ICommunicationService] = None
        self.b_is_initialized = False
        self.b_last_known_service_state = False

    def initialize(self, config_path: str, comm_service: ICommunicationService):
        if comm_service is None:
            raise ValueError("CommService is None")

        # JSONファイルからPduChannelConfigを生成
        pdu_config = PduChannelConfig(config_path)

        # CommunicationBufferにPduChannelConfigを渡して初期化
        self.comm_buffer = CommunicationBuffer(pdu_config)
        self.comm_service = comm_service
        self.b_is_initialized = True
        print("[INFO] PduManager initialized")

    def is_service_enabled(self) -> bool:
        if not self.b_is_initialized or self.comm_service is None:
            return False
        current_state = self.comm_service.is_service_enabled()
        self.b_last_known_service_state = current_state
        return current_state

    def start_service(self, uri: str = "") -> bool:
        if not self.b_is_initialized or self.comm_service is None:
            return False
        if self.comm_service.is_service_enabled():
            return False
        result = self.comm_service.start_service(self.comm_buffer, uri)
        self.b_last_known_service_state = result
        return result

    def stop_service(self) -> bool:
        if not self.b_is_initialized or self.comm_service is None:
            return False
        result = self.comm_service.stop_service()
        self.b_last_known_service_state = not result
        return result

    def get_pdu_channel_id(self, robot_name: str, pdu_name: str) -> int:
        return self.comm_buffer.get_pdu_channel_id(robot_name, pdu_name)

    def get_pdu_size(self, robot_name: str, pdu_name: str) -> int:
        return self.comm_buffer.get_pdu_size(robot_name, pdu_name)

    def flush_pdu_raw_data(self, robot_name: str, pdu_name: str, pdu_raw_data: bytearray) -> bool:
        if not self.is_service_enabled() or self.comm_service is None:
            return False
        channel_id = self.comm_buffer.get_pdu_channel_id(robot_name, pdu_name)
        if channel_id < 0:
            return False
        return self.comm_service.send_data(robot_name, channel_id, pdu_raw_data)

    def read_pdu_raw_data(self, robot_name: str, pdu_name: str) -> Optional[bytearray]:
        if not self.is_service_enabled():
            return None
        return self.comm_buffer.get_buffer(robot_name, pdu_name)

    def declare_pdu_for_read(self, robot_name: str, pdu_name: str) -> bool:
        return self._declare_pdu(robot_name, pdu_name, is_read=True)

    def declare_pdu_for_write(self, robot_name: str, pdu_name: str) -> bool:
        return self._declare_pdu(robot_name, pdu_name, is_read=False)

    def declare_pdu_for_readwrite(self, robot_name: str, pdu_name: str) -> bool:
        return (self.declare_pdu_for_read(robot_name, pdu_name) and
                self.declare_pdu_for_write(robot_name, pdu_name))

    def _declare_pdu(self, robot_name: str, pdu_name: str, is_read: bool) -> bool:
        if not self.is_service_enabled():
            return False

        channel_id = self.comm_buffer.get_pdu_channel_id(robot_name, pdu_name)
        if channel_id < 0:
            return False

        magic_number = 0x52455044 if is_read else 0x57505044
        pdu_raw_data = bytearray(magic_number.to_bytes(4, byteorder='little'))
        return self.comm_service.send_data(robot_name, channel_id, pdu_raw_data)

    def log_current_state(self):
        print("PduManager State:")
        print(f"  - Initialized: {self.b_is_initialized}")
        print(f"  - CommBuffer Valid: {self.comm_buffer is not None}")
        print(f"  - CommService Valid: {self.comm_service is not None}")
        print(f"  - Last Known Service State: {self.b_last_known_service_state}")
