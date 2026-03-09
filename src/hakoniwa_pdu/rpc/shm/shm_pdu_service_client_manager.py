from hakoniwa_pdu._optional_hakopy import hakopy
from typing import Optional

from .shm_pdu_service_base_manager import ShmPduServiceBaseManager
from ..ipdu_service_manager import (
    IPduServiceClientManagerImmediate,
    ClientId,
    PduData,
    Event,
)
from ..service_config import ServiceConfig
from ..async_shared.profile import ScopedTimer


class ShmPduServiceClientManager(
    ShmPduServiceBaseManager, IPduServiceClientManagerImmediate
):
    """共有メモリ向けクライアント実装"""

    def register_client(self, service_name: str, client_name: str) -> Optional[ClientId]:
        with ScopedTimer(
            f"ShmPduServiceClientManager.register_client service={service_name} client={client_name}"
        ):
            if self.service_config is None:
                if self.service_config_path is None or self.offmap is None:
                    raise RuntimeError("service manager is not initialized")
                self.service_config = ServiceConfig(
                    self.service_config_path,
                    self.offmap,
                    hakopy=hakopy,
                )
            if not self._shared_memory_loaded:
                self.load_shared_memory_for_safe(self.pdu_config.get_pdudef())
                self._shared_memory_loaded = True
            with ScopedTimer(
                f"ShmPduServiceClientManager.register_client.asset_service_client_create service={service_name} client={client_name}"
            ):
                handle = hakopy.asset_service_client_create(
                    self.asset_name, service_name, client_name
                )
            if handle is None:
                return None

            with ScopedTimer(
                f"ShmPduServiceClientManager.register_client.prepare_service_pdudef_once service={service_name} client={client_name}"
            ):
                self.prepare_service_pdudef_once()

            client_id = self.allocate_client_handle_id()
            with ScopedTimer(
                f"ShmPduServiceClientManager.register_client.asset_service_get_channel_id service={service_name} client={client_name}"
            ):
                ids = hakopy.asset_service_get_channel_id(handle["service_id"], handle["client_id"])
            if ids is None:
                raise RuntimeError("Failed to get channel IDs")
            self.request_channel_id, self.response_channel_id = ids
            with ScopedTimer(
                f"ShmPduServiceClientManager.register_client.create_client_context service={service_name} client={client_name}"
            ):
                self.client_handles[client_id] = self._create_client_context(handle, ids)
            return client_id

    def _create_client_context(self, handle, ids):
        request_channel_id, response_channel_id = ids
        from .shm_pdu_service_base_manager import ShmClientHandleContext

        return ShmClientHandleContext(
            handle=handle,
            service_id=handle["service_id"],
            native_client_id=handle["client_id"],
            request_channel_id=request_channel_id,
            response_channel_id=response_channel_id,
        )

    def get_request_buffer(
        self, client_id: int, opcode: int, poll_interval_msec: int, request_id: int
    ) -> bytes:
        byte_array = hakopy.asset_service_client_get_request_buffer(
            self.get_client_context(client_id).handle, opcode, poll_interval_msec
        )
        if byte_array is None:
            raise Exception("Failed to get request byte array")
        return byte_array

    def call_request(
        self, client_id: ClientId, pdu_data: PduData, timeout_msec: int
    ) -> bool:
        context = self.get_client_context(client_id)
        return hakopy.asset_service_client_call_request(
            context.handle, pdu_data, timeout_msec
        )

    def poll_response(self, client_id: ClientId) -> Event:
        self.sleep(self.delta_time_sec)
        return self.poll_response_nowait(client_id)

    def poll_response_nowait(self, client_id: ClientId) -> Event:
        context = self.get_client_context(client_id)
        return hakopy.asset_service_client_poll(context.handle)

    def get_response(self, service_name: str, client_id: ClientId) -> PduData:
        context = self.get_client_context(client_id)
        raw_data = hakopy.asset_service_client_get_response(context.handle, -1)
        if raw_data is None or len(raw_data) == 0:
            raise RuntimeError("Failed to read response packet")
        return raw_data

    def cancel_request(self, client_id: ClientId) -> bool:
        context = self.get_client_context(client_id)
        return hakopy.asset_service_client_cancel_request(context.handle)

    # --- クライアントイベント種別判定 ---
    def is_client_event_response_in(self, event: Event) -> bool:
        return event == hakopy.HAKO_SERVICE_CLIENT_API_EVENT_RESPONSE_IN

    def is_client_event_timeout(self, event: Event) -> bool:
        return event == hakopy.HAKO_SERVICE_CLIENT_API_EVENT_REQUEST_TIMEOUT

    def is_client_event_cancel_done(self, event: Event) -> bool:
        return event == hakopy.HAKO_SERVICE_CLIENT_API_EVENT_REQUEST_CANCEL_DONE

    def is_client_event_none(self, event: Event) -> bool:
        return event == hakopy.HAKO_SERVICE_CLIENT_API_EVENT_NONE

    @property
    def requires_external_request_id(self) -> bool:
        return False


__all__ = ["ShmPduServiceClientManager"]
