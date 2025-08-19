import asyncio
from typing import Callable, Awaitable, Any
from .ipdu_service_manager import IPduServiceManager

# リクエストハンドラの型定義: async def handler(request) -> response
RequestHandler = Callable[[Any], Awaitable[Any]]

class ServerProtocol:
    """
    IPduServiceManagerを介してサーバーのRPCプロトコルを処理するクラス。
    """
    def __init__(self, pdu_manager: IPduServiceManager, req_decoder: Callable, res_encoder: Callable):
        """
        サーバープロトコルハンドラを初期化する。

        Args:
            pdu_manager: IPduServiceManagerを実装したインスタンス。
            req_decoder: リクエストPDUをデコードする関数 (bytes -> dict)。
            res_encoder: レスポンスPDUをエンコードする関数 (dict -> bytes)。
        """
        self.pdu_manager = pdu_manager
        self.req_decoder = req_decoder
        self.res_encoder = res_encoder
        self._is_serving = False

    async def serve(self, handler: RequestHandler, cancel_handler: RequestHandler = None, poll_interval: float = 0.01):
        """
        サーバーのメインイベントループを開始する。

        Args:
            handler: リクエストを処理する非同期コールバック関数。
            cancel_handler: (オプション) キャンセル要求を処理する非同期コールバック関数。
            poll_interval: イベントがない場合のポーリング間隔（秒）。
        """
        self._is_serving = True
        print("Server protocol started...")
        while self._is_serving:
            event = self.pdu_manager.poll_request()

            if self.pdu_manager.is_server_event_request_in(event):
                client_id, req_pdu_data = self.pdu_manager.get_request()
                print(f"Request received from client {client_id}")
                
                try:
                    # PDUをデコードし、ハンドラを呼び出し、レスポンスをエンコードする
                    request_data = self.req_decoder(req_pdu_data)
                    response_data = await handler(request_data)
                    res_pdu_data = self.res_encoder(response_data)

                    # レスポンスを送信
                    self.pdu_manager.put_response(client_id, res_pdu_data)
                    print(f"Response sent to client {client_id}")
                except Exception as e:
                    print(f"Error processing request from client {client_id}: {e}")

            elif self.pdu_manager.is_server_event_cancel(event) and cancel_handler:
                client_id, req_pdu_data = self.pdu_manager.get_request()
                print(f"Cancel request received from client {client_id}")
                try:
                    request_data = self.req_decoder(req_pdu_data)
                    response_data = await cancel_handler(request_data)
                    res_pdu_data = self.res_encoder(response_data)

                    self.pdu_manager.put_cancel_response(client_id, res_pdu_data)
                    print(f"Cancel response sent to client {client_id}")
                except Exception as e:
                    print(f"Error processing cancel request from client {client_id}: {e}")

            elif self.pdu_manager.is_server_event_none(event):
                await asyncio.sleep(poll_interval)
            
            else:
                print(f"Unhandled server event: {event}")

    def stop(self):
        """
        サーバーのイベントループを停止する。
        """
        self._is_serving = False
        print("Server protocol stopping...")
