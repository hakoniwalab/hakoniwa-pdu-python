import hakopy
from typing import Any, Tuple, Optional, Dict

from .ipdu_service_manager import IPduServiceManager, ClientId, PduData, Event
from .service_config import ServiceConfig
from hakoniwa_pdu.impl.shm_communication_service import ShmCommunicationService
from hakoniwa_pdu.impl.hako_binary import offset_map

class ShmPduServiceManager(IPduServiceManager):
    """
    IPduServiceManagerインターフェースの共有メモリ（SHM）向け実装。
    内部でhakopyライブラリを呼び出す。
    """

    def __init__(self, asset_name: str, pdu_config_path: str, offset_path: str):
        """
        ShmPduServiceManagerを初期化する（第1段階：安全な初期化）。

        Args:
            asset_name: アセット名。
            pdu_config_path: pdu_config.jsonのパス。
            offset_path: オフセットファイルのディレクトリパス。
        """
        super().__init__()
        self.asset_name = asset_name
        self.offset_path = offset_path

        # PduManagerの基本的な初期化
        self.initialize(config_path=pdu_config_path, comm_service=ShmCommunicationService())
        self.start_service_nowait()

        # サービス関連のコンフィグはまだ初期化しない
        self.service_config: Optional[ServiceConfig] = None
        self.service_id_map: Dict[int, str] = {}  # service_id -> service_name
        self.client_handles: Dict[ClientId, Any] = {}  # client_id -> hakopy handle
        self.current_server_client_info: Dict[str, Any] = {}

    def initialize_services(self, service_config_path: str) -> int:
        self.service_config_path = service_config_path
        return hakopy.service_initialize(self.service_config_path)

    # --- サーバー側操作 ---

    def start_service(self, service_name: str, max_clients: int) -> bool:
        offmap = offset_map.create_offmap(self.offset_path)
        self.service_config = ServiceConfig(self.service_config_path, offmap, hakopy=hakopy)

        # サービス用のPDU定義を既存の定義に追記
        pdudef = self.service_config.append_pdu_def(self.pdu_config.get_pdudef())
        self.pdu_config.update_pdudef(pdudef)
        print("Service PDU definitions prepared.")
        service_id = hakopy.asset_service_create(self.asset_name, service_name)
        if service_id < 0:
            return False
        self.service_id_map[service_id] = service_name
        return True

    def poll_request(self) -> Event:
        # 複数のサービスを管理する場合、どのサービスをポーリングするかの指定が必要だが、
        # ここでは最初に作られたサービスを対象とする簡易的な実装とする。
        if not self.service_id_map:
            raise RuntimeError("No service started.")
        service_id = list(self.service_id_map.keys())[0]
        
        event = hakopy.asset_service_server_poll(service_id)
        if self.is_server_event_request_in(event) or self.is_server_event_cancel(event):
            client_id = hakopy.asset_service_server_get_current_client_id(service_id)
            req_id, res_id = hakopy.asset_service_server_get_current_channel_id(service_id)
            self.current_server_client_info = {
                'service_id': service_id,
                'client_id': client_id,
                'req_channel_id': req_id,
                'res_channel_id': res_id
            }
        return event


    def get_request(self) -> Tuple[ClientId, PduData]:
        if not self.current_server_client_info:
            raise RuntimeError("No active request. Call poll_request() first.")
        info = self.current_server_client_info
        service_id = info['service_id']
        service_name = self.service_id_map.get(service_id)
        if service_name is None:
            raise RuntimeError(f"Unknown service_id: {service_id}")

        pdu_name = self.pdu_config.get_pdu_name(service_name, info['req_channel_id'])
        
        self.run_nowait()  # PDUバッファを更新
        print(f'service_name: {service_name}, pdu_name: {pdu_name}')
        pdu_data = self.read_pdu_raw_data(service_name, pdu_name)
        #print(f"Request PDU data: {pdu_data}")
        return (info['client_id'], pdu_data)

    def put_response(self, client_id: ClientId, pdu_data: PduData) -> bool:
        service_id = self.current_server_client_info.get('service_id')
        return hakopy.asset_service_server_put_response(service_id, pdu_data)

    def put_cancel_response(self, client_id: ClientId, pdu_data: PduData) -> bool:
        # 現状の実装ではput_responseと同じだが、エンコーダ側でヘッダのresult_codeを変える想定
        return self.put_response(client_id, pdu_data)

    # --- クライアント側操作 ---

    def register_client(self, service_name: str, client_name: str) -> Optional[ClientId]:
        handle = hakopy.asset_service_client_create(self.asset_name, service_name, client_name)
        if handle is None:
            return None
        client_id = handle['client_id']
        self.client_handles[client_id] = handle
        return client_id

    def call_request(self, client_id: ClientId, pdu_data: PduData, timeout_msec: int) -> bool:
        handle = self.client_handles.get(client_id)
        if not handle:
            raise ValueError(f"Invalid client_id: {client_id}")
        return hakopy.asset_service_client_call_request(handle, pdu_data, timeout_msec)

    def poll_response(self, client_id: ClientId) -> Event:
        handle = self.client_handles.get(client_id)
        if not handle:
            raise ValueError(f"Invalid client_id: {client_id}")
        return hakopy.asset_service_client_poll(handle)

    def get_response(self, client_id: ClientId) -> PduData:
        handle = self.client_handles.get(client_id)
        if not handle:
            raise ValueError(f"Invalid client_id: {client_id}")
        return hakopy.asset_service_client_get_response(handle, -1)

    def cancel_request(self, client_id: ClientId) -> bool:
        handle = self.client_handles.get(client_id)
        if not handle:
            raise ValueError(f"Invalid client_id: {client_id}")
        return hakopy.asset_service_client_cancel_request(handle)

    # --- サーバーイベント種別判定 ---

    def is_server_event_request_in(self, event: Event) -> bool:
        return event == hakopy.HAKO_SERVICE_SERVER_API_EVENT_REQUEST_IN

    def is_server_event_cancel(self, event: Event) -> bool:
        return event == hakopy.HAKO_SERVICE_SERVER_API_EVENT_CANCEL

    def is_server_event_none(self, event: Event) -> bool:
        return event == hakopy.HAKO_SERVICE_SERVER_API_EVENT_NONE

    # --- クライアントイベント種別判定 ---

    def is_client_event_response_in(self, event: Event) -> bool:
        return event == hakopy.HAKO_SERVICE_CLIENT_API_EVENT_RESPONSE_IN

    def is_client_event_timeout(self, event: Event) -> bool:
        return event == hakopy.HAKO_SERVICE_CLIENT_API_EVENT_REQUEST_TIMEOUT

    def is_client_event_cancel_done(self, event: Event) -> bool:
        return event == hakopy.HAKO_SERVICE_CLIENT_API_EVENT_REQUEST_CANCEL_DONE

    def is_client_event_none(self, event: Event) -> bool:
        return event == hakopy.HAKO_SERVICE_CLIENT_API_EVENT_NONE
