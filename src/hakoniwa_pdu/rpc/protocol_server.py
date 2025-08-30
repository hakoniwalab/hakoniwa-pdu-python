import asyncio
import time
from dataclasses import dataclass
from typing import Callable, Awaitable, Any, Type, Union, Dict, Optional

from .ipdu_service_manager import (
    IPduServiceServerManagerImmediate,
    IPduServiceServerManagerBlocking,
)

RequestHandler = Callable[[Any], Awaitable[Any]]

PduManagerType = Union[
    IPduServiceServerManagerImmediate,
    IPduServiceServerManagerBlocking,
]


@dataclass
class _ServiceContext:
    max_clients: int
    cls_req_packet: Type[Any]
    req_encoder: Callable
    req_decoder: Callable
    cls_res_packet: Type[Any]
    res_encoder: Callable
    res_decoder: Callable
    handler: Optional[RequestHandler] = None


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
        self.pdu_manager = pdu_manager
        self.service_name = service_name  # for backward compatibility
        self._primary_service = service_name
        self.services: Dict[str, _ServiceContext] = {}
        self.add_service(
            service_name,
            max_clients,
            cls_req_packet,
            req_encoder,
            req_decoder,
            cls_res_packet,
            res_encoder,
            res_decoder,
        )
        self._is_serving = False

    def add_service(
        self,
        service_name: str,
        max_clients: int,
        cls_req_packet: Type[Any],
        req_encoder: Callable,
        req_decoder: Callable,
        cls_res_packet: Type[Any],
        res_encoder: Callable,
        res_decoder: Callable,
        handler: Optional[RequestHandler] = None,
    ) -> None:
        self.services[service_name] = _ServiceContext(
            max_clients,
            cls_req_packet,
            req_encoder,
            req_decoder,
            cls_res_packet,
            res_encoder,
            res_decoder,
            handler,
        )
        if hasattr(self.pdu_manager, "req_decoders"):
            self.pdu_manager.req_decoders[service_name] = req_decoder

    async def _handle_request(
        self, ctx: _ServiceContext, client_id: Any, req_pdu_data: bytes
    ) -> bytes:
        request_data = ctx.req_decoder(req_pdu_data)
        if ctx.handler is None:
            raise RuntimeError("No handler registered for service")
        response_data = await ctx.handler(request_data.body)
        byte_array = self.pdu_manager.get_response_buffer(
            client_id,
            self.pdu_manager.API_STATUS_DONE,
            self.pdu_manager.API_RESULT_CODE_OK,
        )
        print(f"[DEBUG] _handle_request: got response buffer of {len(byte_array)} bytes")
        r = ctx.res_decoder(byte_array)
        r.body = response_data
        print(f"[DEBUG] _handle_request: got response PDU")
        res_pdu_data = ctx.res_encoder(r)
        print(f"[DEBUG] _handle_request: encoded response PDU of {len(res_pdu_data)} bytes")
        return res_pdu_data


class ProtocolServerBlocking(ProtocolServerBase):
    """Blocking (async/await) RPC protocol server."""

    async def start_service(self) -> bool:
        ctx = self.services[self._primary_service]
        self.pdu_manager.register_req_serializer(
            ctx.cls_req_packet, ctx.req_encoder, ctx.req_decoder
        )
        self.pdu_manager.register_res_serializer(
            ctx.cls_res_packet, ctx.res_encoder, ctx.res_decoder
        )
        return await self.pdu_manager.start_rpc_service(
            self._primary_service, max_clients=ctx.max_clients
        )

    async def start_services(self) -> bool:
        for name, ctx in self.services.items():
            self.pdu_manager.register_req_serializer(
                ctx.cls_req_packet, ctx.req_encoder, ctx.req_decoder
            )
            self.pdu_manager.register_res_serializer(
                ctx.cls_res_packet, ctx.res_encoder, ctx.res_decoder
            )
            if not await self.pdu_manager.start_rpc_service(
                name, max_clients=ctx.max_clients
            ):
                return False
        return True

    async def serve(
        self,
        handlers: Union[RequestHandler, Dict[str, RequestHandler]],
        poll_interval: float = 0.01,
    ) -> None:
        if callable(handlers):
            handlers = {self._primary_service: handlers}
        for name, handler in handlers.items():
            if name in self.services:
                self.services[name].handler = handler
            else:
                raise RuntimeError(f"Handler specified for unknown service '{name}'")

        self._is_serving = True
        while self._is_serving:
            service_name, event = await self.pdu_manager.poll_request()
            if service_name is not None:
                ctx = self.services.get(service_name)
                if ctx is None:
                    if self.pdu_manager.is_server_event_none(event):
                        await asyncio.sleep(poll_interval)
                    else:
                        print(f"service_name: {service_name}")
                        print(f"services: {self.services}")
                        print(f"Unhandled server event: {event}")
                    continue

                self.pdu_manager.register_req_serializer(
                    ctx.cls_req_packet, ctx.req_encoder, ctx.req_decoder
                )
                self.pdu_manager.register_res_serializer(
                    ctx.cls_res_packet, ctx.res_encoder, ctx.res_decoder
                )

            if self.pdu_manager.is_server_event_request_in(event):
                client_id, req_pdu_data = self.pdu_manager.get_request()
                try:
                    res_pdu_data = await self._handle_request(
                        ctx, client_id, req_pdu_data
                    )
                    await self.pdu_manager.put_response(client_id, res_pdu_data)
                except Exception as e:
                    print(f"Error processing request from client {client_id}: {e}")
            elif self.pdu_manager.is_server_event_cancel(event):
                client_id, req_pdu_data = self.pdu_manager.get_request()
                try:
                    print(f'before cancel request from client {client_id}')
                    await self.pdu_manager.put_cancel_response(client_id, None)
                    print(f'after cancel request from client {client_id}')
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
        ctx = self.services[self._primary_service]
        self.pdu_manager.register_req_serializer(
            ctx.cls_req_packet, ctx.req_encoder, ctx.req_decoder
        )
        self.pdu_manager.register_res_serializer(
            ctx.cls_res_packet, ctx.res_encoder, ctx.res_decoder
        )
        return self.pdu_manager.start_rpc_service(
            self._primary_service, max_clients=ctx.max_clients
        )

    def start_services(self) -> bool:
        for name, ctx in self.services.items():
            self.pdu_manager.register_req_serializer(
                ctx.cls_req_packet, ctx.req_encoder, ctx.req_decoder
            )
            self.pdu_manager.register_res_serializer(
                ctx.cls_res_packet, ctx.res_encoder, ctx.res_decoder
            )
            if not self.pdu_manager.start_rpc_service(
                name, max_clients=ctx.max_clients
            ):
                return False
        return True

    def serve(
        self,
        handlers: Union[RequestHandler, Dict[str, RequestHandler]],
        poll_interval: float = 0.01,
    ) -> None:
        if callable(handlers):
            handlers = {self._primary_service: handlers}
        for name, handler in handlers.items():
            if name in self.services:
                self.services[name].handler = handler
            else:
                raise RuntimeError(f"Handler specified for unknown service '{name}'")

        self._is_serving = True
        while self._is_serving:
            service_name, event = self.pdu_manager.poll_request()
            if service_name is not None:
                ctx = self.services.get(service_name)
                if ctx is None:
                    if self.pdu_manager.is_server_event_none(event):
                        time.sleep(poll_interval)
                    else:
                        print(f"Unhandled server event: {event}")
                    continue

                self.pdu_manager.register_req_serializer(
                    ctx.cls_req_packet, ctx.req_encoder, ctx.req_decoder
                )
                self.pdu_manager.register_res_serializer(
                    ctx.cls_res_packet, ctx.res_encoder, ctx.res_decoder
                )

            if self.pdu_manager.is_server_event_request_in(event):
                client_id, req_pdu_data = self.pdu_manager.get_request()
                try:
                    res_pdu_data = asyncio.run(
                        self._handle_request(ctx, client_id, req_pdu_data)
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
