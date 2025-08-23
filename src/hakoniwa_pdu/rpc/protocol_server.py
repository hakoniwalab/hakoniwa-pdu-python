import asyncio
import time
from typing import Callable, Awaitable, Any, Type
from .ipdu_service_manager import IPduServiceManager

# リクエストハンドラの型定義: async def handler(request) -> response
RequestHandler = Callable[[Any], Awaitable[Any]]

class ProtocolServer:
    """
    IPduServiceManagerを介してサーバーのRPCプロトコルを処理するクラス。
    """
    def __init__(self, service_name: str, max_clients: int, pdu_manager: IPduServiceManager, cls_req_packet: Type[Any], req_encoder: Callable, req_decoder: Callable, cls_res_packet: Type[Any], res_encoder: Callable, res_decoder: Callable):
        self.service_name = service_name
        self.max_clients = max_clients
        self.pdu_manager = pdu_manager
        self.cls_req_packet = cls_req_packet
        self.cls_res_packet = cls_res_packet
        self.req_encoder = req_encoder
        self.req_decoder = req_decoder
        self.res_encoder = res_encoder
        self.res_decoder = res_decoder
        self._is_serving = False
        self.pdu_manager.register_req_serializer(cls_req_packet, req_encoder, req_decoder)
        self.pdu_manager.register_res_serializer(cls_res_packet, res_encoder, res_decoder)
    
    async def start_service(self) -> bool:
        return await self.pdu_manager.start_rpc_service(self.service_name, max_clients=self.max_clients)
    
    def start_service_nowait(self) -> bool:
        return self.pdu_manager.start_rpc_service_nowait(self.service_name, max_clients=self.max_clients)

    async def _handle_request(self, client_id: Any, req_pdu_data: bytes, handler: RequestHandler) -> bytes:
        """リクエスト処理の共通ロジック"""
        request_data = self.req_decoder(req_pdu_data)
        response_data = await handler(request_data.body)
        byte_array = self.pdu_manager.get_response_buffer(client_id, self.pdu_manager.API_STATUS_DONE, self.pdu_manager.API_RESULT_CODE_OK)
        r = self.res_decoder(byte_array)
        r.body = response_data
        res_pdu_data = self.res_encoder(r)
        return res_pdu_data

    async def serve(self, handler: RequestHandler, poll_interval: float = 0.01):
        """
        サーバーのメインイベントループを開始する (async版)。
        """
        self._is_serving = True
        print("Server protocol started (async)...")
        while self._is_serving:
            print("[DEBUG] serve: polling request...")
            event = await self.pdu_manager.poll_request()
            print(f"[DEBUG] serve: polled event {event}")

            if self.pdu_manager.is_server_event_request_in(event):
                client_id, req_pdu_data = self.pdu_manager.get_request()
                print(f"Request received from client {client_id}")
                try:
                    res_pdu_data = await self._handle_request(client_id, req_pdu_data, handler)
                    await self.pdu_manager.put_response(client_id, res_pdu_data)
                    print(f"Response sent to client {client_id}")
                except Exception as e:
                    print(f"Error processing request from client {client_id}: {e}")

            elif self.pdu_manager.is_server_event_cancel(event):
                client_id, req_pdu_data = self.pdu_manager.get_request()
                print(f"Cancel request received from client {client_id}")
                try:
                    await self.pdu_manager.put_cancel_response(client_id, None)
                    print(f"Cancel response sent to client {client_id}")
                except Exception as e:
                    print(f"Error processing cancel request from client {client_id}: {e}")

            elif self.pdu_manager.is_server_event_none(event):
                print(f"[DEBUG] serve: no event poll_interval={poll_interval}")
                await asyncio.sleep(poll_interval)
                print(f"[DEBUG] serve: woke up from sleep")
            
            else:
                print(f"Unhandled server event: {event}")

    def serve_nowait(self, handler: RequestHandler, poll_interval: float = 0.01):
        """
        サーバーのメインイベントループを開始する (nowait版)。
        """
        self._is_serving = True
        print("Server protocol started (nowait)...")
        while self._is_serving:
            event = self.pdu_manager.poll_request_nowait()

            if self.pdu_manager.is_server_event_request_in(event):
                client_id, req_pdu_data = self.pdu_manager.get_request()
                print(f"Request received from client {client_id}")
                try:
                    res_pdu_data = asyncio.run(self._handle_request(client_id, req_pdu_data, handler))
                    self.pdu_manager.put_response_nowait(client_id, res_pdu_data)
                    print(f"Response sent to client {client_id}")
                except Exception as e:
                    print(f"Error processing request from client {client_id}: {e}")

            elif self.pdu_manager.is_server_event_cancel(event):
                client_id, req_pdu_data = self.pdu_manager.get_request()
                print(f"Cancel request received from client {client_id}")
                try:
                    self.pdu_manager.put_cancel_response_nowait(client_id, None)
                    print(f"Cancel response sent to client {client_id}")
                except Exception as e:
                    print(f"Error processing cancel request from client {client_id}: {e}")

            elif self.pdu_manager.is_server_event_none(event):
                time.sleep(poll_interval)
            
            else:
                print(f"Unhandled server event: {event}")

    def stop(self):
        """
        サーバーのイベントループを停止する。
        """
        self._is_serving = False
        print("Server protocol stopping...")
