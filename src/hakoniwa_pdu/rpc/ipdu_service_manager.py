from abc import ABC, abstractmethod
from hakoniwa_pdu.pdu_manager import PduManager
from typing import Any, Tuple, Optional, Callable, Type

# 型エイリアスを定義
ClientId = Any
PduData = bytearray
PyPduData = Any  # Python側でのPDUデータ形式

Event = Any  # poll結果として返される、実装依存のイベントオブジェクト

class IPduServiceManager(PduManager, ABC):
    """
    RPCサービスのプロトコル層(client_protocol, server_protocol)が利用するための、
    通信方式(SHM, Remote)に依存しない低レベル操作を定義するインターフェース。
    """
    def register_req_serializer(self, cls_req_packet: Type[Any], req_encoder: Callable, req_decoder: Callable) -> None:
        """
        クライアントのリクエストPDUをエンコード/デコードする関数を登録する。

        Args:
            req_encoder: リクエストPDUをエンコードする関数 (dict -> bytes)。
            req_decoder: リクエストPDUをデコードする関数 (bytes -> dict)。
        """
        self.cls_req_packet = cls_req_packet
        self.req_encoder = req_encoder
        self.req_decoder = req_decoder

    def register_res_serializer(self, cls_res_packet: Type[Any], res_encoder: Callable, res_decoder: Callable) -> None:
        """
        クライアントのレスポンスPDUをエンコード/デコードする関数を登録する。

        Args:
            res_encoder: レスポンスPDUをエンコードする関数 (dict -> bytes)。
            res_decoder: レスポンスPDUをデコードする関数 (bytes -> dict)。
        """
        self.cls_res_packet = cls_res_packet
        self.res_encoder = res_encoder
        self.res_decoder = res_decoder

    # --- サーバー側操作 ---
    @abstractmethod
    def initialize_services(self, service_config_path: str, delta_time_usec: int) -> int:
        pass

    @abstractmethod
    def start_rpc_service_nowait(self, service_name: str, max_clients: int) -> bool:
        pass

    @abstractmethod
    async def start_rpc_service(self, service_name: str, max_clients: int) -> bool:
        """
        サーバーとしてサービスを開始する。

        Args:
            service_name: 公開するサービス名。
            max_clients: 最大クライアント数。

        Returns:
            成功した場合はTrue。
        """
        pass

    @abstractmethod
    def sleep(self, time_sec: float) -> bool:
        pass

    # constants

    # ====== [ Common API Status / Result Codes ] ======
    API_STATUS_NONE       = 0
    API_STATUS_DOING      = 1
    API_STATUS_CANCELING  = 2
    API_STATUS_DONE       = 3
    API_STATUS_ERROR      = 4

    API_RESULT_CODE_OK       = 0
    API_RESULT_CODE_ERROR    = 1
    API_RESULT_CODE_CANCELED = 2
    API_RESULT_CODE_INVALID  = 3
    API_RESULT_CODE_BUSY     = 4

    # ====== [ Client Opcode ] ======
    CLIENT_API_OPCODE_REQUEST = 0
    CLIENT_API_OPCODE_CANCEL  = 1

    # ====== [ Client Events ] ======
    CLIENT_API_EVENT_NONE              = 0
    CLIENT_API_EVENT_RESPONSE_IN       = 1
    CLIENT_API_EVENT_REQUEST_TIMEOUT   = 2
    CLIENT_API_EVENT_REQUEST_CANCEL_DONE = 3

    # ====== [ Client State ] ======
    CLIENT_API_STATE_IDLE      = 0
    CLIENT_API_STATE_DOING     = 1
    CLIENT_API_STATE_CANCELING = 2

    # ====== [ Server Events ] ======
    SERVER_API_EVENT_NONE         = 0
    SERVER_API_EVENT_REQUEST_IN   = 1
    SERVER_API_EVENT_REQUEST_CANCEL = 2

    # ====== [ Server Status ] ======
    SERVER_API_STATUS_IDLE      = 0
    SERVER_API_STATUS_DOING     = 1
    SERVER_API_STATUS_CANCELING = 2

    # ====== [ Trigger Events ] ======
    TRIGGER_EVENT_ID_START = 0
    TRIGGER_EVENT_ID_STOP  = 1
    TRIGGER_EVENT_ID_RESET = 2

    @abstractmethod
    def get_response_buffer(self, client_id: ClientId, status: int, result_code: int) -> Optional[PduData]:
        """
        指定されたクライアントのレスポンスバッファを取得する。

        Args:
            client_id: クライアントID。
            status: ステータスコード。
            result_code: 結果コード。

        Returns:
            レスポンスPDUデータ。取得できなかった場合はNone。
        """
        pass

    @abstractmethod
    async def poll_request(self) -> Event:
        """
        サーバー側でクライアントからのイベント（リクエスト受信、キャンセル要求など）をポーリングする。

        Returns:
            発生したイベントを示すオブジェクト。
        """
        pass

    @abstractmethod
    def poll_request_nowait(self) -> Event:
        """
        サーバー側でクライアントからのイベントをポーリングする（nowait版）。
        """
        pass

    @abstractmethod
    def get_request(self) -> Tuple[ClientId, PduData]:
        """
        受信したリクエストデータを取得する。
        poll_request()でリクエスト受信イベントを確認した後に呼び出す。

        Returns:
            (クライアントID, リクエストPDUデータ) のタプル。
        """
        pass

    @abstractmethod
    async def put_response(self, client_id: ClientId, pdu_data: PduData) -> bool:
        """
        指定されたクライアントに正常応答PDUを送信する。

        Args:
            client_id: 送信先クライアントのID。
            pdu_data: 送信するレスポンスPDUデータ。
        """
        pass

    @abstractmethod
    def put_response_nowait(self, client_id: ClientId, pdu_data: PduData) -> bool:
        """
        指定されたクライアントに正常応答PDUを送信する（nowait版）。

        Args:
            client_id: 送信先クライアントのID。
            pdu_data: 送信するレスポンスPDUデータ。
        """
        pass

    @abstractmethod
    async def put_cancel_response(self, client_id: ClientId, pdu_data: PduData) -> bool:
        """
        指定されたクライアントにキャンセル応答PDUを送信する。

        Args:
            client_id: 送信先クライアントのID。
            pdu_data: 送信するレスポンスPDUデータ。
        """
        pass

    @abstractmethod
    def put_cancel_response_nowait(self, client_id: ClientId, pdu_data: PduData) -> bool:
        """
        指定されたクライアントにキャンセル応答PDUを送信する（nowait版）。

        Args:
            client_id: 送信先クライアントのID。
            pdu_data: 送信するレスポンスPDUデータ。
        """
        pass

    # --- サーバーイベント種別判定 ---

    @abstractmethod
    def is_server_event_request_in(self, event: Event) -> bool:
        """サーバー：リクエスト受信イベントか"""
        pass

    @abstractmethod
    def is_server_event_cancel(self, event: Event) -> bool:
        """サーバー：キャンセル要求イベントか"""
        pass

    @abstractmethod
    def is_server_event_none(self, event: Event) -> bool:
        """サーバー：イベントが発生しなかったか"""
        pass

    # --- クライアント側操作 ---

    @abstractmethod
    async def register_client(self, service_name: str, client_name: str) -> Optional[ClientId]:
        pass
    
    @abstractmethod
    def register_client_nowait(self, service_name: str, client_name: str) -> Optional[ClientId]:
        """
        クライアントとしてサービスに登録する。

        Args:
            service_name: 接続先のサービス名。
            client_name: 自身のクライアント名。

        Returns:
            成功した場合はクライアントID、失敗した場合はNone。
        """
        pass

    @abstractmethod
    async def call_request(self, client_id: ClientId, pdu_data: PduData, timeout_msec: int) -> bool:
        """
        サービスにリクエストPDUを送信する。

        Args:
            client_id: 登録時に取得したクライアントID。
            pdu_data: 送信するリクエストPDUデータ。
            timeout_msec: タイムアウト（ミリ秒）。
        """
        pass

    @abstractmethod
    def call_request_nowait(self, client_id: ClientId, pdu_data: PduData, timeout_msec: int) -> bool:
        """
        サービスにリクエストPDUを送信する（非同期）。

        Args:
            client_id: 登録時に取得したクライアントID。
            pdu_data: 送信するリクエストPDUデータ。
            timeout_msec: タイムアウト（ミリ秒）。

        Returns:
            成功した場合はTrue、失敗した場合はFalse。
        """
        pass

    @abstractmethod
    def get_request_buffer(self, client_id: int, opcode: int, poll_interval_msec: int) -> bytes:
        pass

    @abstractmethod
    def poll_response(self, client_id: ClientId) -> Event:
        """
        クライアント側でサーバーからのイベント（レスポンス受信、タイムアウトなど）をポーリングする。

        Args:
            client_id: 登録時に取得したクライアントID。

        Returns:
            発生したイベントを示すオブジェクト。
        """
        pass

    @abstractmethod
    def get_response(self, client_id: ClientId) -> PduData:
        """
        受信したレスポンスPDUデータを取得する。
        poll_response()でレスポンス受信イベントを確認した後に呼び出す。

        Args:
            client_id: 登録時に取得したクライアントID。
        """
        pass

    @abstractmethod
    async def cancel_request(self, client_id: ClientId) -> bool:
        """
        送信済みのリクエストのキャンセルを要求する。

        Args:
            client_id: 登録時に取得したクライアントID。
        """
        pass

    @abstractmethod
    def cancel_request_nowait(self, client_id: ClientId) -> bool:
        pass

    # --- クライアントイベント種別判定 ---

    @abstractmethod
    def is_client_event_response_in(self, event: Event) -> bool:
        """クライアント：レスポンス受信イベントか"""
        pass

    @abstractmethod
    def is_client_event_timeout(self, event: Event) -> bool:
        """クライアント：タイムアウトイベントか"""
        pass

    @abstractmethod
    def is_client_event_cancel_done(self, event: Event) -> bool:
        """クライアント：キャンセル完了イベントか"""
        pass

    @abstractmethod
    def is_client_event_none(self, event: Event) -> bool:
        """クライアント：イベントが発生しなかったか"""
        pass
