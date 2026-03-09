from __future__ import annotations

from typing import Any, Callable, Type

from .profile import ScopedTimer
from .rpc_call_future import RpcCallFuture
from .shared_rpc_runtime import RegisteredClientContext, SharedRpcRuntime


class AsyncRpcClientHandle:
    """Logical RPC client on top of SharedRpcRuntime."""

    def __init__(
        self,
        *,
        runtime: SharedRpcRuntime,
        service_name: str,
        client_name: str,
        cls_req_packet: Type[Any],
        req_encoder: Callable,
        req_decoder: Callable,
        cls_res_packet: Type[Any],
        res_encoder: Callable,
        res_decoder: Callable,
    ) -> None:
        self.runtime = runtime
        self.service_name = service_name
        self.client_name = client_name
        self.cls_req_packet = cls_req_packet
        self.req_encoder = req_encoder
        self.req_decoder = req_decoder
        self.cls_res_packet = cls_res_packet
        self.res_encoder = res_encoder
        self.res_decoder = res_decoder
        self.client_context: RegisteredClientContext | None = None
        self._client_instance_request_id_counter = 0

        self.runtime.manager.register_req_serializer(
            cls_req_packet, req_encoder, req_decoder
        )
        self.runtime.manager.register_res_serializer(
            cls_res_packet, res_encoder, res_decoder
        )

    def register(self) -> bool:
        with ScopedTimer(
            f"AsyncRpcClientHandle.register service={self.service_name} client={self.client_name}"
        ):
            self.client_context = self.runtime.register_client(
                self.service_name, self.client_name, res_decoder=self.res_decoder
            )
        return True

    def _create_request_packet(
        self, request_data: Any, poll_interval: float
    ) -> tuple[int, bytes]:
        if self.client_context is None:
            raise RuntimeError("Client is not registered. Call register() first.")

        manager = self.runtime.manager
        manager.register_req_serializer(
            self.cls_req_packet, self.req_encoder, self.req_decoder
        )
        manager.register_res_serializer(
            self.cls_res_packet, self.res_encoder, self.res_decoder
        )
        if hasattr(manager, "service_name"):
            manager.service_name = self.service_name
        if hasattr(manager, "client_name"):
            manager.client_name = self.client_name

        request_id_to_pass = -1
        if manager.requires_external_request_id:
            request_id_to_pass = self._client_instance_request_id_counter
            self._client_instance_request_id_counter += 1

        poll_interval_msec = int(poll_interval * 1000)
        byte_array = manager.get_request_buffer(
            self.client_context.client_id,
            manager.CLIENT_API_OPCODE_REQUEST,
            poll_interval_msec,
            request_id=request_id_to_pass,
        )
        if byte_array is None:
            raise RuntimeError("Failed to get request byte array")

        req_packet = self.req_decoder(byte_array)
        actual_request_id = req_packet.header.request_id
        req_packet.body = request_data
        req_pdu_data = self.req_encoder(req_packet)
        return actual_request_id, req_pdu_data

    def call_async(
        self,
        request_data: Any,
        *,
        timeout_msec: int = 1000,
        poll_interval: float = 0.01,
    ) -> RpcCallFuture:
        if self.client_context is None:
            raise RuntimeError("Client is not registered. Call register() first.")

        request_id, req_pdu_data = self._create_request_packet(
            request_data, poll_interval
        )
        future = self.runtime.create_future(
            service_id=self.client_context.service_id,
            client_id=self.client_context.client_id,
            request_id=request_id,
        )

        if not self.runtime.manager.call_request(
            self.client_context.client_id, req_pdu_data, timeout_msec
        ):
            self.runtime.fail_future(
                service_id=self.client_context.service_id,
                client_id=self.client_context.client_id,
                request_id=request_id,
                exc=RuntimeError(
                    f"Failed to send request: service={self.service_name} client={self.client_name}"
                ),
            )
        return future

    def call(
        self,
        request_data: Any,
        *,
        timeout_msec: int = 1000,
        poll_interval: float = 0.01,
        timeout: float | None = None,
    ) -> Any:
        future = self.call_async(
            request_data,
            timeout_msec=timeout_msec,
            poll_interval=poll_interval,
        )
        return future.result(timeout=timeout)
