import asyncio
import time
from typing import Any, Callable, Type, Optional, Union

from .ipdu_service_manager import (
    IPduServiceClientManagerImmediate,
    IPduServiceClientManagerBlocking,
    ClientId,
)

PduManagerType = Union[IPduServiceClientManagerImmediate, IPduServiceClientManagerBlocking]


class ProtocolClientBase:
    """Common functionality for RPC protocol clients."""

    def __init__(
        self,
        pdu_manager: PduManagerType,
        service_name: str,
        client_name: str,
        cls_req_packet: Type[Any],
        req_encoder: Callable,
        req_decoder: Callable,
        cls_res_packet: Type[Any],
        res_encoder: Callable,
        res_decoder: Callable,
    ) -> None:
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
        self.pdu_manager.register_req_serializer(
            cls_req_packet, req_encoder, req_decoder
        )
        self.pdu_manager.register_res_serializer(
            cls_res_packet, res_encoder, res_decoder
        )

    def _create_request_packet(self, request_data: Any, poll_interval: float) -> bytes:
        if self.client_id is None:
            raise RuntimeError("Client is not registered. Call register() first.")

        self.pdu_manager.register_req_serializer(
            self.cls_req_packet, self.req_encoder, self.req_decoder
        )
        self.pdu_manager.register_res_serializer(
            self.cls_res_packet, self.res_encoder, self.res_decoder
        )
        # Ensure the manager uses the correct service/client identifiers
        if hasattr(self.pdu_manager, "service_name"):
            self.pdu_manager.service_name = self.service_name
        if hasattr(self.pdu_manager, "client_name"):
            self.pdu_manager.client_name = self.client_name

        request_id_to_pass = -1
        if self.pdu_manager.requires_external_request_id:
            current_request_id = self._client_instance_request_id_counter
            self._client_instance_request_id_counter += 1
            request_id_to_pass = current_request_id
            self._client_instance_last_request_id = current_request_id

        poll_interval_msec = int(poll_interval * 1000)
        byte_array = self.pdu_manager.get_request_buffer(
            self.client_id,
            self.pdu_manager.CLIENT_API_OPCODE_REQUEST,
            poll_interval_msec,
            request_id=request_id_to_pass,
        )

        if byte_array is None:
            raise Exception("Failed to get request byte array")

        req_packet = self.req_decoder(byte_array)

        if not self.pdu_manager.requires_external_request_id:
            self._client_instance_last_request_id = req_packet.header.request_id

        req_packet.body = request_data
        req_pdu_data = self.req_encoder(req_packet)
        return req_pdu_data


class ProtocolClientBlocking(ProtocolClientBase):
    """Blocking (async/await) RPC protocol client."""

    async def start_service(self, uri: str) -> bool:
        return await self.pdu_manager.start_service(uri=uri)

    async def register(self) -> bool:
        self.client_id = await self.pdu_manager.register_client(
            self.service_name, self.client_name
        )
        if self.client_id is not None:
            print(
                f"Client '{self.client_name}' registered with service '{self.service_name}' (ID: {self.client_id})"
            )
            return True
        print(f"Failed to register client '{self.client_name}'")
        return False

    async def _wait_response(self) -> tuple[bool, Any]:
        while True:
            event = self.pdu_manager.poll_response(self.client_id)
            if self.pdu_manager.is_client_event_response_in(event):
                res_pdu_data = self.pdu_manager.get_response(
                    self.service_name, self.client_id
                )
                response_data = self.res_decoder(res_pdu_data)
                if (
                    response_data.header.request_id
                    != self._client_instance_last_request_id
                ):
                    print(
                        f"Warning: Mismatched request_id. Expected {self._client_instance_last_request_id}, got {response_data.header.request_id}. Discarding."
                    )
                    continue
                return False, response_data.body
            if self.pdu_manager.is_client_event_timeout(event):
                return True, None
            if self.pdu_manager.is_client_event_cancel_done(event):
                return False, None
            if self.pdu_manager.is_client_event_none(event):
                await asyncio.sleep(0.01)

    async def call(
        self,
        request_data: Any,
        timeout_msec: int = 1000,
        poll_interval: float = 0.01,
    ) -> Any:
        req_pdu_data = self._create_request_packet(request_data, poll_interval)

        if not await self.pdu_manager.call_request(
            self.client_id, req_pdu_data, timeout_msec
        ):
            print("Failed to send request.")
            return None

        is_timeout, response_data = await self._wait_response()
        if is_timeout:
            print("Request timed out.")
            await self.cancel()
            return None
        return response_data

    async def cancel(self) -> bool:
        if self.client_id is None:
            raise RuntimeError("Client is not registered.")

        if not await self.pdu_manager.cancel_request(self.client_id):
            raise Exception("Failed to cancel request.")
        _, _ = await self._wait_response()
        return True


class ProtocolClientImmediate(ProtocolClientBase):
    """Immediate (nowait) RPC protocol client."""

    def start_service(self, uri: str) -> bool:
        return self.pdu_manager.start_service_nowait(uri=uri)

    def register(self) -> bool:
        self.client_id = self.pdu_manager.register_client(
            self.service_name, self.client_name
        )
        if self.client_id is not None:
            print(
                f"Client '{self.client_name}' registered with service '{self.service_name}' (ID: {self.client_id})"
            )
            return True
        print(f"Failed to register client '{self.client_name}'")
        return False

    def _wait_response(self) -> tuple[bool, Any]:
        while True:
            event = self.pdu_manager.poll_response(self.client_id)
            if self.pdu_manager.is_client_event_response_in(event):
                res_pdu_data = self.pdu_manager.get_response(
                    self.service_name, self.client_id
                )
                response_data = self.res_decoder(res_pdu_data)
                if (
                    response_data.header.request_id
                    != self._client_instance_last_request_id
                ):
                    print(
                        f"Warning: Mismatched request_id. Expected {self._client_instance_last_request_id}, got {response_data.header.request_id}. Discarding."
                    )
                    continue
                return False, response_data.body
            if self.pdu_manager.is_client_event_timeout(event):
                return True, None
            if self.pdu_manager.is_client_event_cancel_done(event):
                return False, None
            if self.pdu_manager.is_client_event_none(event):
                time.sleep(0.01)

    def call(
        self,
        request_data: Any,
        timeout_msec: int = 1000,
        poll_interval: float = 0.01,
    ) -> Any:
        req_pdu_data = self._create_request_packet(request_data, poll_interval)

        if not self.pdu_manager.call_request(
            self.client_id, req_pdu_data, timeout_msec
        ):
            print("Failed to send request.")
            return None

        is_timeout, response_data = self._wait_response()
        if is_timeout:
            self.cancel()
            return None
        return response_data

    def cancel(self) -> bool:
        if self.client_id is None:
            raise RuntimeError("Client is not registered.")

        if not self.pdu_manager.cancel_request(self.client_id):
            raise Exception("Failed to cancel request.")
        _, _ = self._wait_response()
        return True


__all__ = [
    "ProtocolClientBase",
    "ProtocolClientBlocking",
    "ProtocolClientImmediate",
]
