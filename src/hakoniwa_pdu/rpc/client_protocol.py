import asyncio
from typing import Any, Callable
from .ipdu_service_manager import IPduServiceManager, ClientId

class ClientProtocol:
    """
    IPduServiceManagerを介してクライアントのRPCプロトコルを処理するクラス。
    """
    def __init__(self, pdu_manager: IPduServiceManager, service_name: str, client_name: str, req_encoder: Callable, res_decoder: Callable):
        """
        クライアントプロトコルハンドラを初期化する。

        Args:
            pdu_manager: IPduServiceManagerを実装したインスタンス。
            service_name: 接続先のサービス名。
            client_name: このクライアントの名称。
            req_encoder: リクエストPDUをエンコードする関数 (dict -> bytes)。
            res_decoder: レスポンスPDUをデコードする関数 (bytes -> dict)。
        """
        self.pdu_manager = pdu_manager
        self.service_name = service_name
        self.client_name = client_name
        self.req_encoder = req_encoder
        self.res_decoder = res_decoder
        self.client_id: ClientId = None

    def register(self) -> bool:
        """
        クライアントをサービスに登録する。リクエスト送信前に呼び出す必要がある。

        Returns:
            登録に成功した場合はTrue。
        """
        self.client_id = self.pdu_manager.register_client(self.service_name, self.client_name)
        if self.client_id is not None:
            print(f"Client '{self.client_name}' registered with service '{self.service_name}' (ID: {self.client_id})")
            return True
        else:
            print(f"Failed to register client '{self.client_name}'")
            return False

    async def call(self, request_data: Any, timeout_msec: int = 1000, poll_interval: float = 0.01) -> Any:
        """
        サービスに対して同期的な呼び出し（リクエスト-レスポンス）を行う。

        Args:
            request_data: 送信するリクエストデータ (dictなど)。
            timeout_msec: タイムアウト（ミリ秒）。
            poll_interval: イベントがない場合のポーリング間隔（秒）。

        Returns:
            レスポンスデータ。タイムアウトやエラーの場合はNoneを返す。
        """
        if self.client_id is None:
            raise RuntimeError("Client is not registered. Call register() first.")

        req_pdu_data = self.req_encoder(request_data)
        
        if not self.pdu_manager.call_request(self.client_id, req_pdu_data, timeout_msec):
            print("Failed to send request.")
            return None

        # TODO: タイムアウト処理をより厳密に実装する
        while True:
            event = self.pdu_manager.poll_response(self.client_id)

            if self.pdu_manager.is_client_event_response_in(event):
                res_pdu_data = self.pdu_manager.get_response(self.client_id)
                response_data = self.res_decoder(res_pdu_data)
                return response_data
            
            if self.pdu_manager.is_client_event_timeout(event):
                print("Request timed out.")
                # タイムアウトした場合、キャンセルを試みる
                await self.cancel()
                return None

            if self.pdu_manager.is_client_event_cancel_done(event):
                print("Request successfully cancelled.")
                return None
            
            if self.pdu_manager.is_client_event_none(event):
                await asyncio.sleep(poll_interval)

    async def cancel(self) -> bool:
        """
        送信済みのリクエストのキャンセルを試みる。
        """
        if self.client_id is None:
            raise RuntimeError("Client is not registered.")
        
        return self.pdu_manager.cancel_request(self.client_id)
