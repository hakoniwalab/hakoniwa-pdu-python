import asyncio
import time
from typing import Callable, Awaitable, Any, Type, Union

from .ipdu_service_manager import (
    IPduServiceServerManagerImmediate,
    IPduServiceServerManagerBlocking,
)

# Request handler type
RequestHandler = Callable[[Any], Awaitable[Any]]

PduManagerType = Union[
    IPduServiceServerManagerImmediate,
    IPduServiceServerManagerBlocking,
]


class ProtocolServerBase:
    """Common functionality for RPC protocol servers."""

    def __init__(
        self,
        service_name: str,
        max_clients: int,
        pdu_manager: PduManagerType,
        cls_req_packet: Type[Any],
        req_encoder: Callable,
        req_decoder: Callable,
        cls_res_packet: Type[Any],
        res_encoder: Callable,
        res_decoder: Callable,
    ) -> None:
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
        self.pdu_manager.register_req_serializer(
            cls_req_packet, req_encoder, req_decoder
        )
        self.pdu_manager.register_res_serializer(
            cls_res_packet, res_encoder, res_decoder
        )

    async def _handle_request(
        self, client_id: Any, req_pdu_data: bytes, handler: RequestHandler
    ) -> bytes:
        request_data = self.req_decoder(req_pdu_data)
        response_data = await handler(request_data.body)
        byte_array = self.pdu_manager.get_response_buffer(
            client_id,
            self.pdu_manager.API_STATUS_DONE,
            self.pdu_manager.API_RESULT_CODE_OK,
        )
        r = self.res_decoder(byte_array)
        r.body = response_data
        res_pdu_data = self.res_encoder(r)
        return res_pdu_data


class ProtocolServerBlocking(ProtocolServerBase):
    """Blocking (async/await) RPC protocol server."""

    async def start_service(self) -> bool:
        return await self.pdu_manager.start_rpc_service(
            self.service_name, max_clients=self.max_clients
        )

    async def serve(
        self, handler: RequestHandler, poll_interval: float = 0.01
    ) -> None:
        self._is_serving = True
        while self._is_serving:
            event = await self.pdu_manager.poll_request()
            if self.pdu_manager.is_server_event_request_in(event):
                client_id, req_pdu_data = self.pdu_manager.get_request()
                try:
                    res_pdu_data = await self._handle_request(
                        client_id, req_pdu_data, handler
                    )
                    await self.pdu_manager.put_response(client_id, res_pdu_data)
                except Exception as e:
                    print(f"Error processing request from client {client_id}: {e}")
            elif self.pdu_manager.is_server_event_cancel(event):
                client_id, req_pdu_data = self.pdu_manager.get_request()
                try:
                    await self.pdu_manager.put_cancel_response(client_id, None)
                except Exception as e:
                    print(f"Error processing cancel request from client {client_id}: {e}")
            elif self.pdu_manager.is_server_event_none(event):
                await asyncio.sleep(poll_interval)
            else:
                print(f"Unhandled server event: {event}")

    def stop(self) -> None:
        self._is_serving = False


class ProtocolServerImmediate(ProtocolServerBase):
    """Immediate (nowait) RPC protocol server."""

    def start_service(self) -> bool:
        return self.pdu_manager.start_rpc_service(
            self.service_name, max_clients=self.max_clients
        )

    def serve(self, handler: RequestHandler, poll_interval: float = 0.01) -> None:
        self._is_serving = True
        while self._is_serving:
            event = self.pdu_manager.poll_request()
            if self.pdu_manager.is_server_event_request_in(event):
                client_id, req_pdu_data = self.pdu_manager.get_request()
                try:
                    res_pdu_data = asyncio.run(
                        self._handle_request(client_id, req_pdu_data, handler)
                    )
                    self.pdu_manager.put_response(client_id, res_pdu_data)
                except Exception as e:
                    print(f"Error processing request from client {client_id}: {e}")
            elif self.pdu_manager.is_server_event_cancel(event):
                client_id, req_pdu_data = self.pdu_manager.get_request()
                try:
                    self.pdu_manager.put_cancel_response(client_id, None)
                except Exception as e:
                    print(f"Error processing cancel request from client {client_id}: {e}")
            elif self.pdu_manager.is_server_event_none(event):
                time.sleep(poll_interval)
            else:
                print(f"Unhandled server event: {event}")

    def stop(self) -> None:
        self._is_serving = False


__all__ = [
    "ProtocolServerBase",
    "ProtocolServerBlocking",
    "ProtocolServerImmediate",
]
