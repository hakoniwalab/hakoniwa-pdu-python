import hakopy
from typing import Optional, Tuple

from .shm_pdu_service_base_manager import ShmPduServiceBaseManager
from ..ipdu_service_manager import (
    IPduServiceServerManagerImmediate,
    ClientId,
    PduData,
    Event,
)
from ..service_config import ServiceConfig
from hakoniwa_pdu.impl.hako_binary import offset_map


class ShmPduServiceServerManager(
    ShmPduServiceBaseManager, IPduServiceServerManagerImmediate
):
    """共有メモリ向けサーバー実装"""

    def start_rpc_service(self, service_name: str, max_clients: int) -> bool:
        print(f"Starting service '{service_name}' with max_clients={max_clients}...")
        super().start_service_nowait(uri="")

        offmap = offset_map.create_offmap(self.offset_path)
        self.service_config = ServiceConfig(self.service_config_path, offmap, hakopy=hakopy)

        pdudef = self.service_config.append_pdu_def(self.pdu_config.get_pdudef())
        self.pdu_config.update_pdudef(pdudef)
        print("Service PDU definitions prepared.")
        service_id = hakopy.asset_service_create(self.asset_name, service_name)
        if service_id < 0:
            return False
        self.service_id_map[service_id] = service_name
        return True

    def poll_request(self) -> Tuple[Optional[str], Event]:
        if not self.service_id_map:
            raise RuntimeError("No service started.")

        # 処理中のリクエストがある場合は同じサービス名でNONEイベントを返す
        if self.current_server_client_info:
            return (
                self.current_server_client_info.get("service_name"),
                hakopy.HAKO_SERVICE_SERVER_API_EVENT_NONE,
            )

        self.sleep(self.delta_time_sec)
        for service_id, service_name in self.service_id_map.items():
            event = hakopy.asset_service_server_poll(service_id)
            if self.is_server_event_request_in(event) or self.is_server_event_cancel(event):
                client_id = hakopy.asset_service_server_get_current_client_id(service_id)
                req_id, res_id = hakopy.asset_service_server_get_current_channel_id(service_id)
                self.current_server_client_info = {
                    "service_id": service_id,
                    "service_name": service_name,
                    "client_id": client_id,
                    "req_channel_id": req_id,
                    "res_channel_id": res_id,
                }
                return service_name, event
        return None, hakopy.HAKO_SERVICE_SERVER_API_EVENT_NONE

    def get_response_buffer(
        self, client_id: ClientId, status: int, result_code: int
    ) -> Optional[PduData]:
        service_id = self.current_server_client_info.get("service_id")
        byte_array = hakopy.asset_service_server_get_response_buffer(
            service_id, status, result_code
        )
        if byte_array is None:
            raise Exception("Failed to get response byte array")
        return byte_array

    def get_request(self) -> Tuple[ClientId, PduData]:
        if not self.current_server_client_info:
            raise RuntimeError("No active request. Call poll_request() first.")
        info = self.current_server_client_info
        service_id = info["service_id"]
        pdu_data = hakopy.asset_service_server_get_request(service_id)
        return (info["client_id"], pdu_data)

    def put_response(self, client_id: ClientId, pdu_data: PduData) -> bool:
        service_id = self.current_server_client_info.get("service_id")
        ret = hakopy.asset_service_server_put_response(service_id, pdu_data)
        if ret:
            self.current_server_client_info = {}
        return ret

    def put_cancel_response(self, client_id: ClientId, pdu_data: PduData) -> bool:
        service_id = self.current_server_client_info.get("service_id")
        ret = hakopy.asset_service_client_cancel_request(service_id, client_id)
        if ret:
            self.current_server_client_info = {}
        return ret

    # --- サーバーイベント種別判定 ---
    def is_server_event_request_in(self, event: Event) -> bool:
        return event == hakopy.HAKO_SERVICE_SERVER_API_EVENT_REQUEST_IN

    def is_server_event_cancel(self, event: Event) -> bool:
        return event == hakopy.HAKO_SERVICE_SERVER_API_EVENT_CANCEL

    def is_server_event_none(self, event: Event) -> bool:
        return event == hakopy.HAKO_SERVICE_SERVER_API_EVENT_NONE


__all__ = ["ShmPduServiceServerManager"]

