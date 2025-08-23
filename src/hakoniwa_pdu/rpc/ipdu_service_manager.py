from abc import ABC, abstractmethod
from typing import Any, Tuple, Optional, Callable, Type

from hakoniwa_pdu.pdu_manager import PduManager

# 型エイリアス
ClientId = Any
PduData = bytearray
PyPduData = Any  # Python側でのPDUデータ形式

Event = Any  # poll結果として返される、実装依存のイベントオブジェクト


class IPduServiceManager(PduManager, ABC):
    """RPCサービス用PDU操作の共通インターフェース"""

    def register_req_serializer(
        self,
        cls_req_packet: Type[Any],
        req_encoder: Callable,
        req_decoder: Callable,
    ) -> None:
        self.cls_req_packet = cls_req_packet
        self.req_encoder = req_encoder
        self.req_decoder = req_decoder

    def register_res_serializer(
        self,
        cls_res_packet: Type[Any],
        res_encoder: Callable,
        res_decoder: Callable,
    ) -> None:
        self.cls_res_packet = cls_res_packet
        self.res_encoder = res_encoder
        self.res_decoder = res_decoder

    # --- サーバー側共通操作 ---
    @abstractmethod
    def initialize_services(self, service_config_path: str, delta_time_usec: int) -> int:
        pass

    @abstractmethod
    def sleep(self, time_sec: float) -> bool:
        pass

    # ====== [ Common API Status / Result Codes ] ======
    API_STATUS_NONE = 0
    API_STATUS_DOING = 1
    API_STATUS_CANCELING = 2
    API_STATUS_DONE = 3
    API_STATUS_ERROR = 4

    API_RESULT_CODE_OK = 0
    API_RESULT_CODE_ERROR = 1
    API_RESULT_CODE_CANCELED = 2
    API_RESULT_CODE_INVALID = 3
    API_RESULT_CODE_BUSY = 4

    # ====== [ Client Opcode ] ======
    CLIENT_API_OPCODE_REQUEST = 0
    CLIENT_API_OPCODE_CANCEL = 1

    # ====== [ Client Events ] ======
    CLIENT_API_EVENT_NONE = 0
    CLIENT_API_EVENT_RESPONSE_IN = 1
    CLIENT_API_EVENT_REQUEST_TIMEOUT = 2
    CLIENT_API_EVENT_REQUEST_CANCEL_DONE = 3

    # ====== [ Client State ] ======
    CLIENT_API_STATE_IDLE = 0
    CLIENT_API_STATE_DOING = 1
    CLIENT_API_STATE_CANCELING = 2

    # ====== [ Server Events ] ======
    SERVER_API_EVENT_NONE = 0
    SERVER_API_EVENT_REQUEST_IN = 1
    SERVER_API_EVENT_REQUEST_CANCEL = 2

    # ====== [ Server Status ] ======
    SERVER_API_STATUS_IDLE = 0
    SERVER_API_STATUS_DOING = 1
    SERVER_API_STATUS_CANCELING = 2

    # ====== [ Trigger Events ] ======
    TRIGGER_EVENT_ID_START = 0
    TRIGGER_EVENT_ID_STOP = 1
    TRIGGER_EVENT_ID_RESET = 2

    @abstractmethod
    def get_response_buffer(
        self, client_id: ClientId, status: int, result_code: int
    ) -> Optional[PduData]:
        pass

    @abstractmethod
    def get_request(self) -> Tuple[ClientId, PduData]:
        pass

    @abstractmethod
    def get_request_buffer(
        self, client_id: int, opcode: int, poll_interval_msec: int, request_id: int
    ) -> bytes:
        pass

    @abstractmethod
    def poll_response(self, client_id: ClientId) -> Event:
        pass

    @abstractmethod
    def get_response(self, service_name: str, client_id: ClientId) -> PduData:
        pass

    # --- サーバーイベント種別判定 ---
    @abstractmethod
    def is_server_event_request_in(self, event: Event) -> bool:
        pass

    @abstractmethod
    def is_server_event_cancel(self, event: Event) -> bool:
        pass

    @abstractmethod
    def is_server_event_none(self, event: Event) -> bool:
        pass

    # --- クライアント側イベント判定 ---
    @abstractmethod
    def is_client_event_response_in(self, event: Event) -> bool:
        pass

    @abstractmethod
    def is_client_event_timeout(self, event: Event) -> bool:
        pass

    @abstractmethod
    def is_client_event_cancel_done(self, event: Event) -> bool:
        pass

    @abstractmethod
    def is_client_event_none(self, event: Event) -> bool:
        pass

    @property
    @abstractmethod
    def requires_external_request_id(self) -> bool:
        pass


class IPduServiceManagerImmediate(IPduServiceManager):
    """nowait系APIを提供する実装が従うインターフェース"""

    # --- サーバー側操作 ---
    @abstractmethod
    def start_rpc_service(self, service_name: str, max_clients: int) -> bool:
        pass

    @abstractmethod
    def poll_request(self) -> Event:
        pass

    @abstractmethod
    def put_response(self, client_id: ClientId, pdu_data: PduData) -> bool:
        pass

    @abstractmethod
    def put_cancel_response(self, client_id: ClientId, pdu_data: PduData) -> bool:
        pass

    # --- クライアント側操作 ---
    @abstractmethod
    def register_client(self, service_name: str, client_name: str) -> Optional[ClientId]:
        pass

    @abstractmethod
    def call_request(
        self, client_id: ClientId, pdu_data: PduData, timeout_msec: int
    ) -> bool:
        pass

    @abstractmethod
    def cancel_request(self, client_id: ClientId) -> bool:
        pass


class IPduServiceManagerBlocking(IPduServiceManager):
    """async/awaitを用いるブロッキングAPIのインターフェース"""

    # --- サーバー側操作 ---
    @abstractmethod
    async def start_rpc_service(self, service_name: str, max_clients: int) -> bool:
        pass

    @abstractmethod
    async def poll_request(self) -> Event:
        pass

    @abstractmethod
    async def put_response(self, client_id: ClientId, pdu_data: PduData) -> bool:
        pass

    @abstractmethod
    async def put_cancel_response(
        self, client_id: ClientId, pdu_data: PduData
    ) -> bool:
        pass

    # --- クライアント側操作 ---
    @abstractmethod
    async def register_client(
        self, service_name: str, client_name: str
    ) -> Optional[ClientId]:
        pass

    @abstractmethod
    async def call_request(
        self, client_id: ClientId, pdu_data: PduData, timeout_msec: int
    ) -> bool:
        pass

    @abstractmethod
    async def cancel_request(self, client_id: ClientId) -> bool:
        pass


__all__ = [
    "ClientId",
    "PduData",
    "PyPduData",
    "Event",
    "IPduServiceManager",
    "IPduServiceManagerImmediate",
    "IPduServiceManagerBlocking",
]

