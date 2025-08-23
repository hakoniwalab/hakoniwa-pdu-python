import hakopy
from typing import Optional

from .shm_pdu_service_base_manager import ShmPduServiceBaseManager
from ..ipdu_service_manager import (
    IPduServiceClientManagerImmediate,
    ClientId,
    PduData,
    Event,
)
from ..service_config import ServiceConfig
from hakoniwa_pdu.impl.hako_binary import offset_map


class ShmPduServiceClientManager(
    ShmPduServiceBaseManager, IPduServiceClientManagerImmediate
):
    """共有メモリ向けクライアント実装"""

    def register_client(self, service_name: str, client_name: str) -> Optional[ClientId]:
        offmap = offset_map.create_offmap(self.offset_path)
        self.service_config = ServiceConfig(self.service_config_path, offmap, hakopy=hakopy)

        pdudef = self.service_config.append_pdu_def(self.pdu_config.get_pdudef())
        self.pdu_config.update_pdudef(pdudef)
        print("Service PDU definitions prepared.")

        handle = hakopy.asset_service_client_create(
            self.asset_name, service_name, client_name
        )
        if handle is None:
            return None
        client_id = handle["client_id"]
        self.client_handles[client_id] = handle
        ids = hakopy.asset_service_get_channel_id(handle["service_id"], handle["client_id"])
        if ids is None:
            raise RuntimeError("Failed to get channel IDs")
        self.request_channel_id, self.response_channel_id = ids
        return client_id

    def get_request_buffer(
        self, client_id: int, opcode: int, poll_interval_msec: int, request_id: int
    ) -> bytes:
        byte_array = hakopy.asset_service_client_get_request_buffer(
            self.client_handles[client_id], opcode, poll_interval_msec
        )
        if byte_array is None:
            raise Exception("Failed to get request byte array")
        return byte_array

    def call_request(
        self, client_id: ClientId, pdu_data: PduData, timeout_msec: int
    ) -> bool:
        handle = self.client_handles.get(client_id)
        if not handle:
            raise ValueError(f"Invalid client_id: {client_id}")
        return hakopy.asset_service_client_call_request(handle, pdu_data, timeout_msec)

    def poll_response(self, client_id: ClientId) -> Event:
        self.sleep(self.delta_time_sec)
        handle = self.client_handles.get(client_id)
        if not handle:
            raise ValueError(f"Invalid client_id: {client_id}")
        return hakopy.asset_service_client_poll(handle)

    def get_response(self, service_name: str, client_id: ClientId) -> PduData:
        handle = self.client_handles.get(client_id)
        if not handle:
            raise ValueError(f"Invalid client_id: {client_id}")
        raw_data = hakopy.asset_service_client_get_response(handle, -1)
        if raw_data is None or len(raw_data) == 0:
            raise RuntimeError("Failed to read response packet")
        return raw_data

    def cancel_request(self, client_id: ClientId) -> bool:
        handle = self.client_handles.get(client_id)
        if not handle:
            raise ValueError(f"Invalid client_id: {client_id}")
        return hakopy.asset_service_client_cancel_request(handle)

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

