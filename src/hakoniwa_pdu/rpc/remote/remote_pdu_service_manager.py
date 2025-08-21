from typing import Any, Tuple, Optional, Dict

from ..ipdu_service_manager import IPduServiceManager, ClientId, PduData, Event
from hakoniwa_pdu.pdu_manager import PduManager
from hakoniwa_pdu.impl.icommunication_service import ICommunicationService
from hakoniwa_pdu.rpc.service_config import ServiceConfig
from hakoniwa_pdu.impl.hako_binary import offset_map


class RemotePduServiceManager(IPduServiceManager):
    """
    Manage remote PDU services for a specific robot.
    """


    def __init__(self, asset_name: str, pdu_config_path: str, offset_path: str, comm_service: ICommunicationService):
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
        self.initialize(config_path=pdu_config_path, comm_service=comm_service)
        self.start_service()

        # サービス関連のコンフィグはまだ初期化しない
        self.service_config: Optional[ServiceConfig] = None
        self.service_id_map: Dict[int, str] = {}  # service_id -> service_name
        self.client_handles: Dict[ClientId, Any] = {}  # client_id -> hakopy handle
        self.current_server_client_info: Dict[str, Any] = {}




    # --- クライアント側操作 ---

    def register_client(self, service_name: str, client_name: str) -> Optional[ClientId]:
        offmap = offset_map.create_offmap(self.offset_path)
        self.service_config = ServiceConfig(self.service_config_path, offmap, hakopy=None)

        # サービス用のPDU定義を既存の定義に追記
        pdudef = self.service_config.append_pdu_def(self.pdu_config.get_pdudef())
        self.pdu_config.update_pdudef(pdudef)
        print("Service PDU definitions prepared.")


        return client_name
