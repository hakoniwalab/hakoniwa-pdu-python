from abc import ABC, abstractmethod
from hakoniwa_pdu.pdu_manager import PduManager
from typing import Any, Tuple, Optional

# 型エイリアスを定義
ClientId = Any
PduData = bytearray
Event = Any  # poll結果として返される、実装依存のイベントオブジェクト

class IPduServiceManager(PduManager, ABC):
    """
    RPCサービスのプロトコル層(client_protocol, server_protocol)が利用するための、
    通信方式(SHM, Remote)に依存しない低レベル操作を定義するインターフェース。
    """

    # --- サーバー側操作 ---

    @abstractmethod
    def start_service(self, service_name: str, max_clients: int) -> bool:
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
    def poll_request(self) -> Event:
        """
        サーバー側でクライアントからのイベント（リクエスト受信、キャンセル要求など）をポーリングする。

        Returns:
            発生したイベントを示すオブジェクト。
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
    def put_response(self, client_id: ClientId, pdu_data: PduData) -> bool:
        """
        指定されたクライアントに正常応答PDUを送信する。

        Args:
            client_id: 送信先クライアントのID。
            pdu_data: 送信するレスポンスPDUデータ。
        """
        pass

    @abstractmethod
    def put_cancel_response(self, client_id: ClientId, pdu_data: PduData) -> bool:
        """
        指定されたクライアントにキャンセル応答PDUを送信する。

        Args:
            client_id: 送信先クライアントのID。
            pdu_data: 送信するレスポンスPDUデータ。
        """
        pass

    # --- クライアント側操作 ---

    @abstractmethod
    def register_client(self, service_name: str, client_name: str) -> Optional[ClientId]:
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
    def call_request(self, client_id: ClientId, pdu_data: PduData, timeout_msec: int) -> bool:
        """
        サービスにリクエストPDUを送信する。

        Args:
            client_id: 登録時に取得したクライアントID。
            pdu_data: 送信するリクエストPDUデータ。
            timeout_msec: タイムアウト（ミリ秒）。
        """
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
    def cancel_request(self, client_id: ClientId) -> bool:
        """
        送信済みのリクエストのキャンセルを要求する。

        Args:
            client_id: 登録時に取得したクライアントID。
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
