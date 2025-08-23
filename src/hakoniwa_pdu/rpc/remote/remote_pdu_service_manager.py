from dataclasses import dataclass
from typing import Any, Tuple, Optional, Dict
import asyncio
import time

from ..ipdu_service_manager import (
    IPduServiceManagerBlocking,
    ClientId,
    PduData,
    PyPduData,
    Event,
)
from hakoniwa_pdu.pdu_manager import PduManager
from hakoniwa_pdu.impl.icommunication_service import ICommunicationService
from hakoniwa_pdu.rpc.service_config import ServiceConfig
from hakoniwa_pdu.impl.hako_binary import offset_map
from hakoniwa_pdu.pdu_msgs.hako_srv_msgs.pdu_pytype_ServiceRequestHeader import ServiceRequestHeader

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
@dataclass
class ClientHandle:
    """
    クライアントハンドルのデータ構造。
    クライアントIDとリクエストチャネルID、レスポンスチャネルIDを保持する。
    """
    client_id: int
    request_channel_id: int
    response_channel_id: int

class ClientRegistry:
    def __init__(self):
        self.clients: Dict[str, ClientHandle] = {}  # client_name -> ClientHandle

class RemotePduServiceManager(IPduServiceManagerBlocking):
    """
    Manage remote PDU services for a specific robot.
    """


    def __init__(self, asset_name: str, pdu_config_path: str, offset_path: str, comm_service: ICommunicationService, uri: str):
        """
        ShmPduServiceManagerを初期化する（第1段階：安全な初期化）。

        Args:
            asset_name: アセット名。
            pdu_config_path: pdu_config.jsonのパス。
            offset_path: オフセットファイルのディレクトリパス。
        """
        super().__init__()
        # Common
        self.asset_name = asset_name
        self.offset_path = offset_path
        self.uri = uri
        self.service_config: Optional[ServiceConfig] = None

        # Server
        self._server_instance_client_registry: Optional[ClientRegistry] = None
        self._server_instance_service_id_map: Dict[int, str] = {}  # service_id -> service_name
        self._server_instance_client_handles: Dict[ClientId, Any] = {}  # client_id -> hakopy handle
        self._server_instance_current_server_client_info: Dict[str, Any] = {}
        self._server_instance_service_name: Optional[str] = None
        self._server_instance_client_name: Optional[str] = None
        self._server_instance_service_config_path: Optional[str] = None
        self._server_instance_delta_time_usec: Optional[int] = None
        self._server_instance_delta_time_sec: Optional[float] = None
        self._server_instance_request_id = 0

        # Client
        self._client_instance_request_id = 0
        self._client_instance_service_name: Optional[str] = None
        self._client_instance_client_name: Optional[str] = None
        self._client_instance_timeout_msec: Optional[int] = None
        self._client_instance_call_start_time_msec: Optional[int] = None
        self._client_instance_request_buffer: Optional[bytes] = None
        self._client_instance_poll_interval_msec: Optional[int] = None

        # PduManagerの基本的な初期化
        comm_service.register_event_handler(self.handler)
        self.initialize(config_path=pdu_config_path, comm_service=comm_service)


    async def _handler_register_client(self, packet: DataPacket) -> None:
        body_raw_data = packet.body_data
        body_pdu_data = pdu_to_py_RegisterClientRequestPacket(body_raw_data)
        service_id = self.service_config.get_service_index(body_pdu_data.header.service_name)
        if self._server_instance_client_registry is None:
            self._server_instance_client_registry = ClientRegistry()
        if self._server_instance_client_registry.clients.get(body_pdu_data.header.client_name) is not None:
            raise ValueError(f"Client registry for service '{body_pdu_data.header.service_name}' already exists")

        # RPCクライアント登録
        client_id = len(self._server_instance_client_registry.clients)
        request_channel_id = (client_id * 2)
        response_channel_id = (client_id * 2) + 1
        client_handle = ClientHandle(
            client_id=client_id,
            request_channel_id=request_channel_id,
            response_channel_id=response_channel_id
        )
        self._server_instance_client_registry.clients[body_pdu_data.header.client_name] = client_handle

        print(f'[DEBUG] Registered RPC client: {body_pdu_data.header.client_name}')
        # 応答パケット作成
        register_client_res_packet: RegisterClientResponsePacket = RegisterClientResponsePacket()
        register_client_res_packet.header.request_id = 0
        register_client_res_packet.header.service_name = body_pdu_data.header.service_name
        register_client_res_packet.header.client_name = body_pdu_data.header.client_name
        register_client_res_packet.header.result_code = self.API_RESULT_CODE_OK
        register_client_res_packet.body.client_id = client_handle.client_id
        register_client_res_packet.body.service_id = service_id
        register_client_res_packet.body.request_channel_id = client_handle.request_channel_id
        register_client_res_packet.body.response_channel_id = client_handle.response_channel_id

        # 応答送信
        pdu_data = py_to_pdu_RegisterClientResponsePacket(register_client_res_packet)
        raw_data = self._build_binary(PDU_DATA_RPC_REPLY, body_pdu_data.header.service_name, client_handle.response_channel_id, pdu_data)
        if not await self.comm_service.send_binary(raw_data):
            raise RuntimeError("Failed to send register client response")
        print(f'[DEBUG] Sent register client response: {body_pdu_data.header.client_name}')
        return None
    
    async def handler(self, packet: DataPacket) -> None:
        """
        ハンドラ関数。受信したパケットを処理する。
        """
        if packet.meta_pdu.meta_request_type == DECLARE_PDU_FOR_READ:
            # 読み取り用のPDU宣言
            print(f"Declare PDU for read: {packet.robot_name}, channel_id={packet.channel_id}")
            #TODO
        elif packet.meta_pdu.meta_request_type == DECLARE_PDU_FOR_WRITE:
            # 書き込み用のPDU宣言
            print(f"Declare PDU for write: {packet.robot_name}, channel_id={packet.channel_id}")
            #TODO
        elif packet.meta_pdu.meta_request_type == REGISTER_RPC_CLIENT:
            # RPCクライアント登録
            print(f"Register RPC client: {packet.robot_name}, channel_id={packet.channel_id}")
            await self._handler_register_client(packet)
        else:
            raise NotImplementedError("Unknown packet type")

    # --- サーバー側操作 ---
    def initialize_services(self, service_config_path: str, delta_time_usec: int) -> int:
        self._server_instance_service_config_path = service_config_path
        self._server_instance_delta_time_usec = delta_time_usec
        self._server_instance_delta_time_sec: float = delta_time_usec / 1_000_000.0

    async def start_rpc_service(self, service_name: str, max_clients: int) -> bool:
        offmap = offset_map.create_offmap(self.offset_path)
        self.service_config = ServiceConfig(self._server_instance_service_config_path, offmap, hakopy=None)

        # サービス用のPDU定義を既存の定義に追記
        pdudef = self.service_config.append_pdu_def(self.pdu_config.get_pdudef())
        self.pdu_config.update_pdudef(pdudef)
        print("Service PDU definitions prepared.")
        self._server_instance_service_name = service_name
        return await super().start_service(uri=self.uri)

    def sleep(self, time_sec: float) -> bool:
        time.sleep(time_sec)
        return True

    def get_response_buffer(self, client_id: ClientId, status: int, result_code: int) -> Optional[PduData]:
        py_pdu_data = self.cls_res_packet()
        py_pdu_data.header.request_id = self._server_instance_request_id
        py_pdu_data.header.service_name = self._server_instance_service_name
        py_pdu_data.header.client_name = self._server_instance_client_name
        py_pdu_data.header.status = status
        py_pdu_data.header.processing_percentage = 100
        py_pdu_data.header.result_code = result_code
        pdu_data = self.res_encoder(py_pdu_data)
        return pdu_data

    async def poll_request(self) -> Event:
        print(f"[DEBUG] poll_request start")
        if self._server_instance_client_name is not None:
            #複数のクライアントの同時リクエストはサポートしない
            return self.SERVER_API_EVENT_NONE
        # await asyncio.sleep(self._server_instance_delta_time_sec)
        #クライアントレジストリを探索して、バッファチェックする
        if self._server_instance_client_registry is None:
            return self.SERVER_API_EVENT_NONE
        for client_name, client_handle in self._server_instance_client_registry.clients.items():
            print(f"[DEBUG] poll_request: checking client {client_name}")
            if self.comm_buffer.contains_buffer(self._server_instance_service_name, client_name):
                raw_data = self.comm_buffer.peek_buffer(self._server_instance_service_name, client_name)
                request = self.req_decoder(raw_data)
                self._server_instance_client_name = client_name
                self._server_instance_request_id = request.header.request_id
                print(f"[DEBUG] poll_request: request found for client {client_name}")
                if request.header.opcode == self.CLIENT_API_OPCODE_CANCEL:
                    return self.SERVER_API_EVENT_REQUEST_CANCEL
                return self.SERVER_API_EVENT_REQUEST_IN
        print(f"[DEBUG] poll_request end: no request found")
        return self.SERVER_API_EVENT_NONE

    def get_request(self) -> Tuple[ClientId, PduData]:
        if self.comm_buffer.contains_buffer(self._server_instance_service_name, self._server_instance_client_name):
            raw_data = self.comm_buffer.get_buffer(self._server_instance_service_name, self._server_instance_client_name)
            client_handle = self._server_instance_client_registry.clients[self._server_instance_client_name]
            return client_handle, raw_data
        raise RuntimeError("No response data available. Call poll_request() first.")

    async def put_response(self, client_id: ClientId, pdu_data: PduData) -> bool:
        client_handle: ClientHandle = client_id
        raw_data = self._build_binary(PDU_DATA_RPC_REPLY, self._server_instance_service_name, client_handle.request_channel_id, pdu_data)
        if not await self.comm_service.send_binary(raw_data):
            self._server_instance_client_name = None
            self._server_instance_request_id = None
            return False
        self._server_instance_client_name = None
        self._server_instance_request_id = None
        return True

    async def put_cancel_response(self, client_id: ClientId, pdu_data: PduData) -> bool:
        client_handle: ClientHandle = client_id
        cancel_pdu_data = self.get_response_buffer(None, self.API_STATUS_DONE, self.API_RESULT_CODE_CANCELED)
        cancel_pdu_raw_data = self.res_encoder(cancel_pdu_data)
        raw_data = self._build_binary(PDU_DATA_RPC_REPLY, self._server_instance_service_name, client_handle.request_channel_id, cancel_pdu_raw_data)
        if not await self.comm_service.send_binary(raw_data):
            self._server_instance_client_name = None
            self._server_instance_request_id = None
            return False
        self._server_instance_client_name = None
        self._server_instance_request_id = None
        return True

    # --- クライアント側操作 ---

    async def register_client(self, service_name: str, client_name: str, timeout: float = 1.0) -> Optional[ClientId]:
        self._client_instance_service_name = service_name
        self._client_instance_client_name = client_name
        offmap = offset_map.create_offmap(self.offset_path)
        # TODO: service_config_path is not initialized for client
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
        if response.header.result_code != IPduServiceManagerBlocking.API_RESULT_CODE_OK:
            print(f"Failed to register client '{client_name}' to service '{service_name}': {response.header.result_code}")
            return None

        return response.body

    async def call_request(self, client_id: ClientId, pdu_data: PduData, timeout_msec: int) -> bool:
        # pdu_dataは、パケット形式になっているので、buildしてラップすればOK。
        self._client_instance_timeout_msec = timeout_msec
        self._client_instance_call_start_time_msec = int(time.time() * 1000)
        client_info: RegisterClientResponse = client_id
        raw_data = self._build_binary(PDU_DATA_RPC_REQUEST, self._client_instance_service_name, client_info.request_channel_id, pdu_data)
        if not await self.comm_service.send_binary(raw_data):
            return False
        self._client_instance_request_buffer = raw_data
        return True

    def get_request_buffer(self, client_id: int, opcode: int, poll_interval_msec: int, request_id: int) -> bytes:
        self._client_instance_poll_interval_msec = poll_interval_msec
        py_pdu_data = self.cls_req_packet()
        py_pdu_data.header.request_id = request_id
        py_pdu_data.header.service_name = self._client_instance_service_name
        py_pdu_data.header.client_name = self._client_instance_client_name
        py_pdu_data.header.opcode = opcode
        py_pdu_data.header.status_poll_interval_msec = poll_interval_msec
        pdu_data = self.req_encoder(py_pdu_data)
        return pdu_data


    def poll_response(self, client_id: ClientId) -> Event:
        #self.sleep(self._client_instance_poll_interval_msec / 1000.0)  # ミリ秒から秒に変換
        #print(f'[DEBUG] poll_response start: service {self._client_instance_service_name}, client {self._client_instance_client_name}')
        if self.comm_buffer.contains_buffer(self._client_instance_service_name, self._client_instance_client_name):
            raw_data = self.comm_buffer.peek_buffer(self._client_instance_service_name, self._client_instance_client_name)
            response = self.res_decoder(raw_data)
            if response.header.result_code == IPduServiceManagerBlocking.API_RESULT_CODE_CANCELED:
                self._client_instance_request_id = self._client_instance_request_id + 1
                return self.CLIENT_API_EVENT_REQUEST_CANCEL_DONE
            self._client_instance_request_id = self._client_instance_request_id + 1
            return self.CLIENT_API_EVENT_RESPONSE_IN
        current_time_msec = int(time.time() * 1000)
        if (current_time_msec - self._client_instance_call_start_time_msec) > self._client_instance_timeout_msec:
            return self.CLIENT_API_EVENT_REQUEST_TIMEOUT
        return self.CLIENT_API_EVENT_NONE

    def get_response(self, service_name: str, client_id: ClientId) -> PduData:
        if self.comm_buffer.contains_buffer(self._client_instance_service_name, self._client_instance_client_name):
            raw_data = self.comm_buffer.get_buffer(self._client_instance_service_name, self._client_instance_client_name)
            return raw_data
        raise RuntimeError("No response data available. Call poll_response() first.")

    async def cancel_request(self, client_id: ClientId) -> bool:
        py_pdu_data = self.req_decoder(self._client_instance_request_buffer)
        py_pdu_data.header.opcode = self.CLIENT_API_OPCODE_CANCEL
        py_pdu_data.header.poll_interval_msec = -1
        pdu_data = self.req_encoder(py_pdu_data)
        if not await self.comm_service.send_binary(pdu_data):
            return False
        self._client_instance_request_buffer = pdu_data
        return True

    # --- サーバーイベント種別判定 ---

    def is_server_event_request_in(self, event: Event) -> bool:
        return event == self.SERVER_API_EVENT_REQUEST_IN

    def is_server_event_cancel(self, event: Event) -> bool:
        return event == self.SERVER_API_EVENT_REQUEST_CANCEL

    def is_server_event_none(self, event: Event) -> bool:
        return event == self.SERVER_API_EVENT_NONE


    # --- クライアントイベント種別判定 ---

    def is_client_event_response_in(self, event: Event) -> bool:
        return event == self.CLIENT_API_EVENT_RESPONSE_IN

    def is_client_event_timeout(self, event: Event) -> bool:
        return event == self.CLIENT_API_EVENT_REQUEST_TIMEOUT

    def is_client_event_cancel_done(self, event: Event) -> bool:
        return event == self.CLIENT_API_EVENT_REQUEST_CANCEL_DONE

    def is_client_event_none(self, event: Event) -> bool:
        return event == self.CLIENT_API_EVENT_NONE
    
    @property
    def requires_external_request_id(self) -> bool:
        return True