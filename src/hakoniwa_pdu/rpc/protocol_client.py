import asyncio

from typing import Any, Callable, Type, Optional
from .ipdu_service_manager import IPduServiceManager, ClientId

class ProtocolClient:
    """
    IPduServiceManagerを介してクライアントのRPCプロトコルを処理するクラス。
    """
    def __init__(self, pdu_manager: IPduServiceManager, service_name: str, client_name: str, cls_req_packet: Type[Any], req_encoder: Callable, req_decoder: Callable, cls_res_packet: Type[Any], res_encoder: Callable, res_decoder: Callable):
        """
        クライアントプロトコルハンドラを初期化する。

        Args:
            pdu_manager: IPduServiceManagerを実装したインスタンス。
            service_name: 接続先のサービス名。
            client_name: このクライアントの名称。
            req_encoder: リクエストPDUをエンコードする関数 (dict -> bytes)。
            req_decoder: リクエストPDUをデコードする関数 (bytes -> dict)。
            res_decoder: レスポンスPDUをデコードする関数 (bytes -> dict)。
        """
        self.pdu_manager = pdu_manager
        self.service_name = service_name
        self.client_name = client_name
        self.cls_req_packet = cls_req_packet
        self.req_encoder = req_encoder
        self.req_decoder = req_decoder
        self.cls_res_packet = cls_res_packet
        self.res_encoder = res_encoder
        self.res_decoder = res_decoder
        self.client_id: Optional[ClientId] = None
        self._client_instance_request_id_counter = 0
        self._client_instance_last_request_id = -1
        self.pdu_manager.register_req_serializer(cls_req_packet, req_encoder, req_decoder)
        self.pdu_manager.register_res_serializer(cls_res_packet, res_encoder, res_decoder)


    async def start_service(self, uri: str) -> bool:
        return await self.pdu_manager.start_service(uri=uri)

    def register_nowait(self) -> bool:
        """
        クライアントをサービスに登録する。リクエスト送信前に呼び出す必要がある。

        Returns:
            登録に成功した場合はTrue。
        """
        self.client_id = self.pdu_manager.register_client_nowait(self.service_name, self.client_name)
        if self.client_id is not None:
            print(f"Client '{self.client_name}' registered with service '{self.service_name}' (ID: {self.client_id})")
            return True
        else:
            print(f"Failed to register client '{self.client_name}'")
            return False

    async def register(self) -> bool:
        """
        クライアントをサービスに登録する。リクエスト送信前に呼び出す必要がある。

        Returns:
            登録に成功した場合はTrue。
        """
        self.client_id = await self.pdu_manager.register_client(self.service_name, self.client_name)
        if self.client_id is not None:
            print(f"Client '{self.client_name}' registered with service '{self.service_name}' (ID: {self.client_id})")
            return True
        else:
            print(f"Failed to register client '{self.client_name}'")
            return False


    def _create_request_packet(self, request_data: Any, poll_interval: float) -> bytes:
        if self.client_id is None:
            raise RuntimeError("Client is not registered. Call register() first.")

        request_id_to_pass = -1 # デフォルト値
        
        # remoteの場合: ProtocolClientがIDを生成して渡す
        if self.pdu_manager.requires_external_request_id:
            current_request_id = self._client_instance_request_id_counter
            self._client_instance_request_id_counter += 1
            request_id_to_pass = current_request_id
            # remoteの場合は、生成したIDを待つべきIDとして保存
            self._client_instance_last_request_id = current_request_id

        poll_interval_msec = int(poll_interval * 1000)
        byte_array = self.pdu_manager.get_request_buffer(
            self.client_id, self.pdu_manager.CLIENT_API_OPCODE_REQUEST, poll_interval_msec, request_id=request_id_to_pass)
        
        if byte_array is None:
            raise Exception("Failed to get request byte array")

        req_packet = self.req_decoder(byte_array)

        # shmの場合: Cライブラリが設定したIDをバッファから読み取り、待つべきIDとして保存
        if not self.pdu_manager.requires_external_request_id:
            self._client_instance_last_request_id = req_packet.header.request_id
        
        # リクエストボディを設定してエンコード
        req_packet.body = request_data
        req_pdu_data = self.req_encoder(req_packet)
        return req_pdu_data

    def _wait_response(self) -> tuple[bool, Any]:
        while True:
            print(f'Polling for response...')
            event = self.pdu_manager.poll_response(self.client_id)

            if self.pdu_manager.is_client_event_response_in(event):
                print(f"Response received successfully.")
                res_pdu_data = self.pdu_manager.get_response(self.service_name, self.client_id)
                response_data = self.res_decoder(res_pdu_data)
                
                if response_data.header.request_id != self._client_instance_last_request_id:
                    print(f"Warning: Mismatched request_id. Expected {self._client_instance_last_request_id}, got {response_data.header.request_id}. Discarding.")
                    continue

                print(f"Decoded response data: {response_data}")
                return False, response_data.body
            
            if self.pdu_manager.is_client_event_timeout(event):
                print("Request timed out.")
                return True, None

            if self.pdu_manager.is_client_event_cancel_done(event):
                print("Request successfully cancelled.")
                return False, None
            
            if self.pdu_manager.is_client_event_none(event):
                pass

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
        req_pdu_data = self._create_request_packet(request_data, poll_interval)

        if not await self.pdu_manager.call_request(self.client_id, req_pdu_data, timeout_msec):
            print("Failed to send request.")
            return None
        print(f"Request sent successfully: {request_data}")


        is_timeout, response_data = self._wait_response()
        if is_timeout:
            await self.cancel()
            return None
        return response_data
    
    def call_nowait(self, request_data: Any, timeout_msec: int = 1000, poll_interval: float = 0.01) -> Any:
        """
        サービスに対して同期的な呼び出し（リクエスト-レスポンス）を行う。

        Args:
            request_data: 送信するリクエストデータ (dictなど)。
            timeout_msec: タイムアウト（ミリ秒）。
            poll_interval: イベントがない場合のポーリング間隔（秒）。

        Returns:
            レスポンスデータ。タイムアウトやエラーの場合はNoneを返す。
        """
        req_pdu_data = self._create_request_packet(request_data, poll_interval)

        if not self.pdu_manager.call_request_nowait(self.client_id, req_pdu_data, timeout_msec):
            print("Failed to send request.")
            return None
        print(f"Request sent successfully: {request_data}")


        is_timeout, response_data = self._wait_response()
        if is_timeout:
            self.cancel_nowait()
            return None
        return response_data

    async def cancel(self) -> bool:
        """
        送信済みのリクエストのキャンセルを試みる。
        """
        if self.client_id is None:
            raise RuntimeError("Client is not registered.")
        
        if not await self.pdu_manager.cancel_request(self.client_id):
            raise Exception("Failed to cancel request.")
        _, _ = self._wait_response()
        return True

    def cancel_nowait(self) -> bool:
        """
        送信済みのリクエストのキャンセルを試みる。
        """
        if self.client_id is None:
            raise RuntimeError("Client is not registered.")

        if not self.pdu_manager.cancel_request_nowait(self.client_id):
            raise Exception("Failed to cancel request.")
        _, _ = self._wait_response()
        return True


