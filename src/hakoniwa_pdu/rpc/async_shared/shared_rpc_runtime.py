from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import threading
from typing import Any, Callable

from ..shm.shm_pdu_service_client_manager import ShmPduServiceClientManager
from .profile import ScopedTimer
from .rpc_call_future import RpcCallFuture


@dataclass(frozen=True)
class SharedRpcRuntimeConfig:
    mode: str = "manual"
    poller_count: int = 1
    dispatch_workers: int = 1
    poll_interval_sec: float = 0.01
    max_pending_requests: int | None = None

    def validate(self) -> None:
        if self.mode not in {"manual", "background"}:
            raise ValueError(f"unsupported mode: {self.mode}")
        if self.poller_count < 1:
            raise ValueError("poller_count must be >= 1")
        if self.dispatch_workers < 1:
            raise ValueError("dispatch_workers must be >= 1")
        if self.poll_interval_sec < 0:
            raise ValueError("poll_interval_sec must be >= 0")
        if self.max_pending_requests is not None and self.max_pending_requests < 1:
            raise ValueError("max_pending_requests must be >= 1")


@dataclass(frozen=True)
class RegisteredClientContext:
    service_name: str
    client_name: str
    service_id: int
    client_id: int
    handle: dict[str, Any]
    res_decoder: Callable[[Any], Any]


@dataclass
class PendingRequest:
    future: RpcCallFuture
    service_id: int
    client_id: int
    request_id: int
    state: str = "DOING"
    cancel_reason: BaseException | None = None


class SharedRpcRuntime:
    """Shared SHM RPC runtime for one Python process."""

    def __init__(
        self,
        *,
        asset_name: str,
        pdu_config_path: str | Path,
        service_config_path: str | Path,
        offset_path: str | Path,
        delta_time_usec: int,
        config: SharedRpcRuntimeConfig | None = None,
    ) -> None:
        self.asset_name = asset_name
        self.pdu_config_path = str(Path(pdu_config_path).resolve())
        self.service_config_path = str(Path(service_config_path).resolve())
        self.offset_path = str(Path(offset_path).resolve())
        self.delta_time_usec = delta_time_usec
        self.config = config or SharedRpcRuntimeConfig()
        self.config.validate()

        self._manager: ShmPduServiceClientManager | None = None
        self._initialized = False
        self._init_lock = threading.Lock()
        self._registration_lock = threading.Lock()
        self._pending_lock = threading.Lock()
        self._poll_lock = threading.Lock()
        self._client_contexts: dict[tuple[str, str], RegisteredClientContext] = {}
        self._pending: dict[tuple[int, int, int], PendingRequest] = {}
        self._pending_by_client: dict[tuple[int, int], PendingRequest] = {}
        self._background_thread: threading.Thread | None = None
        self._background_stop = threading.Event()

    @property
    def manager(self) -> ShmPduServiceClientManager:
        self.initialize()
        assert self._manager is not None
        return self._manager

    def initialize(self) -> None:
        if self._initialized:
            return
        with self._init_lock:
            if self._initialized:
                return
            with ScopedTimer("SharedRpcRuntime.initialize"):
                self._manager = ShmPduServiceClientManager(
                    asset_name=self.asset_name,
                    pdu_config_path=self.pdu_config_path,
                    offset_path=self.offset_path,
                )
                if self._manager.initialize_services(
                    self.service_config_path, self.delta_time_usec
                ) < 0:
                    raise RuntimeError("initialize_services() failed")
            self._initialized = True

    def close(self) -> None:
        self.stop_background_polling()

    def register_client(
        self, service_name: str, client_name: str, *, res_decoder: Callable[[Any], Any]
    ) -> RegisteredClientContext:
        self.initialize()
        key = (service_name, client_name)
        with self._registration_lock:
            ctx = self._client_contexts.get(key)
            if ctx is not None:
                return ctx
            with ScopedTimer(
                f"SharedRpcRuntime.register_client service={service_name} client={client_name}"
            ):
                client_id = self.manager.register_client(service_name, client_name)
                if client_id is None:
                    raise RuntimeError(
                        f"Failed to register client: service={service_name} client={client_name}"
                    )
                handle_context = self.manager.client_handles.get(client_id)
                if handle_context is None:
                    raise RuntimeError(
                        f"Registered client handle not found: service={service_name} client={client_name} client_id={client_id}"
                    )
                service_id = handle_context.service_id
                ctx = RegisteredClientContext(
                    service_name=service_name,
                    client_name=client_name,
                    service_id=service_id,
                    client_id=client_id,
                    handle=handle_context.handle,
                    res_decoder=res_decoder,
                )
                self._client_contexts[key] = ctx
                return ctx

    def create_future(
        self, *, service_id: int, client_id: int, request_id: int
    ) -> RpcCallFuture:
        future = RpcCallFuture(
            service_id=service_id, client_id=client_id, request_id=request_id
        )
        key = (service_id, client_id, request_id)
        client_key = (service_id, client_id)
        with self._pending_lock:
            if self.config.max_pending_requests is not None:
                if len(self._pending) >= self.config.max_pending_requests:
                    raise RuntimeError("max_pending_requests exceeded")
            if client_key in self._pending_by_client:
                raise RuntimeError(
                    f"in-flight request already exists: service_id={service_id} client_id={client_id}"
                )
            pending = PendingRequest(
                future=future,
                service_id=service_id,
                client_id=client_id,
                request_id=request_id,
            )
            self._pending[key] = pending
            self._pending_by_client[client_key] = pending
        return future

    def resolve_future(
        self, *, service_id: int, client_id: int, request_id: int, result: Any
    ) -> bool:
        key = (service_id, client_id, request_id)
        client_key = (service_id, client_id)
        with self._pending_lock:
            pending = self._pending.pop(key, None)
            self._pending_by_client.pop(client_key, None)
        if pending is None:
            return False
        pending.state = "DONE"
        pending.future.set_result(result)
        return True

    def fail_future(
        self,
        *,
        service_id: int,
        client_id: int,
        request_id: int,
        exc: BaseException,
    ) -> bool:
        key = (service_id, client_id, request_id)
        client_key = (service_id, client_id)
        with self._pending_lock:
            pending = self._pending.pop(key, None)
            self._pending_by_client.pop(client_key, None)
        if pending is None:
            return False
        pending.state = "ERROR"
        pending.future.set_exception(exc)
        return True

    def poll_once(self) -> int:
        """Process one polling cycle without sleeping."""
        self.initialize()
        with self._poll_lock:
            processed = 0
            contexts = list(self._client_contexts.values())
            for ctx in contexts:
                event = self.manager.poll_response_nowait(ctx.client_id)
                if self.manager.is_client_event_none(event):
                    continue
                processed += 1
                if self.manager.is_client_event_response_in(event):
                    res_pdu_data = self.manager.get_response(
                        ctx.service_name, ctx.client_id
                    )
                    response_data = ctx.res_decoder(res_pdu_data)
                    self.resolve_future(
                        service_id=ctx.service_id,
                        client_id=ctx.client_id,
                        request_id=response_data.header.request_id,
                        result=response_data.body,
                    )
                    continue
                if self.manager.is_client_event_timeout(event):
                    self._handle_timeout_event(ctx)
                    continue
                if self.manager.is_client_event_cancel_done(event):
                    self._handle_cancel_done_event(ctx)
                    continue
            return processed

    def _get_pending_for_client(
        self, ctx: RegisteredClientContext
    ) -> PendingRequest | None:
        client_key = (ctx.service_id, ctx.client_id)
        with self._pending_lock:
            return self._pending_by_client.get(client_key)

    def _handle_timeout_event(self, ctx: RegisteredClientContext) -> bool:
        pending = self._get_pending_for_client(ctx)
        if pending is None:
            return False
        if pending.state == "CANCELING":
            return False
        cancel_reason = TimeoutError(
            f"request timeout: service={ctx.service_name} client={ctx.client_name}"
        )
        if not self.manager.cancel_request(ctx.client_id):
            return self.fail_future(
                service_id=ctx.service_id,
                client_id=ctx.client_id,
                request_id=pending.request_id,
                exc=RuntimeError(
                    f"failed to cancel timed out request: service={ctx.service_name} client={ctx.client_name}"
                ),
            )
        with self._pending_lock:
            current = self._pending.get(
                (ctx.service_id, ctx.client_id, pending.request_id)
            )
            if current is None:
                return False
            current.state = "CANCELING"
            current.cancel_reason = cancel_reason
        return True

    def _handle_cancel_done_event(self, ctx: RegisteredClientContext) -> bool:
        pending = self._get_pending_for_client(ctx)
        if pending is None:
            return False
        exc = pending.cancel_reason or RuntimeError(
            f"request canceled: service={ctx.service_name} client={ctx.client_name}"
        )
        return self.fail_future(
            service_id=ctx.service_id,
            client_id=ctx.client_id,
            request_id=pending.request_id,
            exc=exc,
        )

    def start_background_polling(self) -> None:
        if self.config.mode != "background":
            raise RuntimeError("background polling is disabled in manual mode")
        if self._background_thread is not None and self._background_thread.is_alive():
            return
        self._background_stop.clear()
        self._background_thread = threading.Thread(
            target=self._background_loop,
            name="shared-rpc-runtime",
            daemon=True,
        )
        self._background_thread.start()

    def stop_background_polling(self) -> None:
        self._background_stop.set()
        if self._background_thread is not None:
            self._background_thread.join(timeout=1.0)
            self._background_thread = None

    def _background_loop(self) -> None:
        while not self._background_stop.is_set():
            self.poll_once()
            if self.config.poll_interval_sec > 0:
                self._background_stop.wait(self.config.poll_interval_sec)
