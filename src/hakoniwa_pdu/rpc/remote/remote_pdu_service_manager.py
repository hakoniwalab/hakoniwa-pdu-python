from typing import Any, Tuple, Optional, Dict
import asyncio

from ..ipdu_service_manager import IPduServiceManager, ClientId, PduData, Event
from hakoniwa_pdu.pdu_manager import PduManager
from hakoniwa_pdu.impl.icommunication_service import ICommunicationService
from hakoniwa_pdu.rpc.service_config import ServiceConfig
from hakoniwa_pdu.impl.hako_binary import offset_map
from hakoniwa_pdu.pdu_msgs.hako_srv_msgs.pdu_pytype_ServiceRequestHeader import ServiceRequestHeader
from hakoniwa_pdu.pdu_msgs.hako_srv_msgs.pdu_conv_ServiceRequestHeader import (
    pdu_to_py_ServiceRequestHeader,
    py_to_pdu_ServiceRequestHeader
)
from hakoniwa_pdu.pdu_msgs.hako_srv_msgs.pdu_pytype_ServiceResponseHeader import ServiceResponseHeader
from hakoniwa_pdu.pdu_msgs.hako_srv_msgs.pdu_pytype_RegisterClientRequestPacket import RegisterClientRequestPacket
from hakoniwa_pdu.pdu_msgs.hako_srv_msgs.pdu_pytype_RegisterClientResponse import RegisterClientResponse
from hakoniwa_pdu.pdu_msgs.hako_srv_msgs.pdu_pytype_RegisterClientResponsePacket import RegisterClientResponsePacket
from hakoniwa_pdu.pdu_msgs.hako_srv_msgs.pdu_conv_RegisterClientRequestPacket import (
    pdu_to_py_RegisterClientRequestPacket,
    py_to_pdu_RegisterClientRequestPacket
)
from hakoniwa_pdu.pdu_msgs.hako_srv_msgs.pdu_conv_RegisterClientResponsePacket import (
    pdu_to_py_RegisterClientResponsePacket,
    py_to_pdu_RegisterClientResponsePacket
)
from hakoniwa_pdu.impl.data_packet import (
    DataPacket,
    DECLARE_PDU_FOR_READ,
    DECLARE_PDU_FOR_WRITE,
    REQUEST_PDU_READ,
    PDU_DATA,
    REGISTER_RPC_CLIENT,
    PDU_DATA_RPC_REQUEST,
    PDU_DATA_RPC_REPLY
)

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


        self.client_request_id = 0



    # --- クライアント側操作 ---

    async def register_client(self, service_name: str, client_name: str, timeout: float = 1.0) -> Optional[ClientId]:
        self.service_name = service_name
        self.client_name = client_name
        offmap = offset_map.create_offmap(self.offset_path)
        self.service_config = ServiceConfig(self.service_config_path, offmap, hakopy=None)

        # サービス用のPDU定義を既存の定義に追記
        pdudef = self.service_config.append_pdu_def(self.pdu_config.get_pdudef())
        self.pdu_config.update_pdudef(pdudef)
        print("Service PDU definitions prepared.")

        register_client_packet = RegisterClientRequestPacket()
        register_client_packet.header.request_id = 0
        register_client_packet.header.service_name = service_name
        register_client_packet.header.client_name = client_name
        register_client_packet.header.opcode = 0 # request
        register_client_packet.header.status_poll_interval_msec = 0 # no poll
        register_client_packet.body.dummy = 0

        pdu_data = py_to_pdu_RegisterClientRequestPacket(register_client_packet)
        raw_data = self._build_binary(REGISTER_RPC_CLIENT, service_name, -1, pdu_data)
        if not await self.comm_service.send_binary(raw_data):
            return None
        # wait for buffer to be filled
        loop = asyncio.get_event_loop()
        end_time = loop.time() + timeout
        response_buffer = None
        while loop.time() < end_time:
            if self.comm_buffer.contains_buffer(service_name, client_name):
                response_buffer = self.comm_buffer.get_buffer(service_name, client_name)
                break
            await asyncio.sleep(0.05)
        if response_buffer is None:
            return None

        response = pdu_to_py_RegisterClientResponsePacket(response_buffer)
        if response.header.result_code != IPduServiceManager.API_RESULT_CODE_OK:
            print(f"Failed to register client '{client_name}' to service '{service_name}': {response.header.result_code}")
            return None

        return response.body

    def register_client_nowait(self, service_name: str, client_name: str) -> Optional[ClientId]:
        raise NotImplementedError("register_client_nowait is not implemented")


    async def call_request(self, client_id: ClientId, pdu_data: PduData, timeout_msec: int) -> bool:
        # pdu_dataは、パケット形式になっているので、buildしてラップすればOK。
        client_info: RegisterClientResponse = ClientId
        raw_data = self._build_binary(PDU_DATA_RPC_REQUEST, self.service_name, client_info.request_channel_id, pdu_data)
        if not await self.comm_service.send_binary(raw_data):
            return False
        return True

    def call_request_nowait(self, client_id: ClientId, pdu_data: PduData, timeout_msec: int) -> bool:
        raise NotImplementedError("call_request_nowait is not implemented")


    def get_request_buffer(self, client_id: int, opcode: int, poll_interval_msec: int) -> bytes:
        header = ServiceRequestHeader()
        header.request_id = self.client_request_id
        header.service_name = self.service_name
        header.client_name = self.client_name
        header.opcode = opcode
        header.status_poll_interval_msec = poll_interval_msec
        pdu_data = py_to_pdu_ServiceRequestHeader(header)
        return pdu_data


    def poll_response(self, client_id: ClientId) -> Event:
        """
        クライアント側でサーバーからのイベント（レスポンス受信、タイムアウトなど）をポーリングする。

        Args:
            client_id: 登録時に取得したクライアントID。

        Returns:
            発生したイベントを示すオブジェクト。
        """
        pass

    def get_response(self, client_id: ClientId) -> PduData:
        """
        受信したレスポンスPDUデータを取得する。
        poll_response()でレスポンス受信イベントを確認した後に呼び出す。

        Args:
            client_id: 登録時に取得したクライアントID。
        """
        pass

    def cancel_request(self, client_id: ClientId) -> bool:
        """
        送信済みのリクエストのキャンセルを要求する。

        Args:
            client_id: 登録時に取得したクライアントID。
        """
        pass



    # --- クライアントイベント種別判定 ---

    def is_client_event_response_in(self, event: Event) -> bool:
        """クライアント：レスポンス受信イベントか"""
        pass

    def is_client_event_timeout(self, event: Event) -> bool:
        """クライアント：タイムアウトイベントか"""
        pass

    def is_client_event_cancel_done(self, event: Event) -> bool:
        """クライアント：キャンセル完了イベントか"""
        pass

    def is_client_event_none(self, event: Event) -> bool:
        """クライアント：イベントが発生しなかったか"""
        pass
