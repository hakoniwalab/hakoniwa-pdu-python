from dataclasses import dataclass
from typing import Dict, Optional, Tuple, Callable
import asyncio

from .remote_pdu_service_base_manager import RemotePduServiceBaseManager
from ..ipdu_service_manager import (
    IPduServiceServerManagerBlocking,
    ClientId,
    PduData,
    PyPduData,
    Event,
)
from ..service_config import ServiceConfig
from hakoniwa_pdu.impl.hako_binary import offset_map
from hakoniwa_pdu.impl.data_packet import (
    DataPacket,
    DECLARE_PDU_FOR_READ,
    DECLARE_PDU_FOR_WRITE,
    REQUEST_PDU_READ,
    REGISTER_RPC_CLIENT,
    PDU_DATA_RPC_REPLY,
)
from hakoniwa_pdu.pdu_msgs.hako_srv_msgs.pdu_pytype_RegisterClientResponsePacket import (
    RegisterClientResponsePacket,
)
from hakoniwa_pdu.pdu_msgs.hako_srv_msgs.pdu_conv_RegisterClientRequestPacket import (
    pdu_to_py_RegisterClientRequestPacket,
)
from hakoniwa_pdu.pdu_msgs.hako_srv_msgs.pdu_conv_RegisterClientResponsePacket import (
    pdu_to_py_RegisterClientResponsePacket,
    py_to_pdu_RegisterClientResponsePacket,
)


@dataclass
class ClientHandle:
    """Handle information for a registered RPC client."""

    client_id: int
    request_channel_id: int
    response_channel_id: int


class ClientRegistry:
    def __init__(self) -> None:
        self.clients: Dict[str, ClientHandle] = {}


class RemotePduServiceServerManager(
    RemotePduServiceBaseManager, IPduServiceServerManagerBlocking
):
    """Server-side implementation for remote RPC."""

    def __init__(
        self,
        asset_name: str,
        pdu_config_path: str,
        offset_path: str,
        comm_service,
        uri: str,
    ) -> None:
        super().__init__(asset_name, pdu_config_path, offset_path, comm_service, uri)
        # マルチサービス対応のためのレジストリと状態管理
        self.service_registries: Dict[str, ClientRegistry] = {}
        self.current_service_name: Optional[str] = None
        self.current_client_name: Optional[str] = None
        self.request_id = 0
        self.req_decoders: Dict[str, Callable] = {}
        comm_service.register_event_handler(self.handler)
        self.topic_service_started = False
        self.rpc_service_started = False

    async def _handler_register_client(self, packet: DataPacket) -> None:
        body_raw_data = packet.body_data
        body_pdu_data = pdu_to_py_RegisterClientRequestPacket(body_raw_data)
        service_name = body_pdu_data.header.service_name
        service_id = self.service_config.get_service_index(service_name)
        registry = self.service_registries.setdefault(service_name, ClientRegistry())
        if registry.clients.get(body_pdu_data.header.client_name) is not None:
            raise ValueError(
                f"Client registry for service '{service_name}' already exists"
            )

        client_id = len(registry.clients)
        request_channel_id = client_id * 2
        response_channel_id = client_id * 2 + 1
        client_handle = ClientHandle(
            client_id=client_id,
            request_channel_id=request_channel_id,
            response_channel_id=response_channel_id,
        )
        registry.clients[body_pdu_data.header.client_name] = client_handle

        print(f"[DEBUG] Registered RPC client: {body_pdu_data.header.client_name}")
        register_client_res_packet = RegisterClientResponsePacket()
        register_client_res_packet.header.request_id = 0
        register_client_res_packet.header.service_name = (
            body_pdu_data.header.service_name
        )
        register_client_res_packet.header.client_name = (
            body_pdu_data.header.client_name
        )
        register_client_res_packet.header.result_code = self.API_RESULT_CODE_OK
        register_client_res_packet.body.client_id = client_handle.client_id
        register_client_res_packet.body.service_id = service_id
        register_client_res_packet.body.request_channel_id = (
            client_handle.request_channel_id
        )
        register_client_res_packet.body.response_channel_id = (
            client_handle.response_channel_id
        )

        pdu_data = py_to_pdu_RegisterClientResponsePacket(register_client_res_packet)
        raw_data = self._build_binary(
            PDU_DATA_RPC_REPLY,
            service_name,
            client_handle.response_channel_id,
            pdu_data,
        )
        if not await self.comm_service.send_binary(raw_data):
            raise RuntimeError("Failed to send register client response")
        print(
            f"[DEBUG] Sent register client response: {body_pdu_data.header.client_name}"
        )

    def register_handler_pdu_for_read(self, handler: Callable) -> None:
        self.pdu_for_read_handler = handler
    def register_handler_pdu_for_write(self, handler: Callable) -> None:
        self.pdu_for_write_handler = handler
    def register_handler_request_pdu_read(self, handler: Callable) -> None:
        self.request_pdu_read_handler = handler

    async def handler(self, packet: DataPacket) -> None:
        if packet.meta_pdu.meta_request_type == DECLARE_PDU_FOR_READ:
            print(
                f"Declare PDU for read: {packet.robot_name}, channel_id={packet.channel_id}"
            )
            if self.pdu_for_read_handler is not None:
                self.pdu_for_read_handler(packet)
        elif packet.meta_pdu.meta_request_type == DECLARE_PDU_FOR_WRITE:
            print(
                f"Declare PDU for write: {packet.robot_name}, channel_id={packet.channel_id}"
            )
            if self.pdu_for_write_handler is not None:
                self.pdu_for_write_handler(packet)
        elif packet.meta_pdu.meta_request_type == REQUEST_PDU_READ:
            print(
                f"Request PDU for read: {packet.robot_name}, channel_id={packet.channel_id}"
            )
            if self.request_pdu_read_handler is not None:
                self.request_pdu_read_handler(packet)
        elif packet.meta_pdu.meta_request_type == REGISTER_RPC_CLIENT:
            print(
                f"Register RPC client: {packet.robot_name}, channel_id={packet.channel_id}"
            )
            await self._handler_register_client(packet)
        else:
            raise NotImplementedError("Unknown packet type")

    async def start_topic_service(self) -> bool:
        if self.rpc_service_started:
            raise RuntimeError("Cannot start topic service after RPC service has started")
        
        offmap = offset_map.create_offmap(self.offset_path)
        self.service_config = ServiceConfig(
            self.service_config_path, offmap, hakopy=None
        )
        pdudef = self.service_config.append_pdu_def(self.pdu_config.get_pdudef())
        self.pdu_config.update_pdudef(pdudef)
        print("Service PDU definitions prepared.")
        if self.topic_service_started or not await super().start_service(uri=self.uri):
            return False
        self.topic_service_started = True
        return True

    async def start_rpc_service(self, service_name: str, max_clients: int) -> bool:
        if self.topic_service_started:
            raise RuntimeError("Cannot start RPC service after topic service has started")
        self.rpc_service_started = True
        if self.service_config is None:
            offmap = offset_map.create_offmap(self.offset_path)
            self.service_config = ServiceConfig(
                self.service_config_path, offmap, hakopy=None
            )
            pdudef = self.service_config.append_pdu_def(self.pdu_config.get_pdudef())
            self.pdu_config.update_pdudef(pdudef)
            print("Service PDU definitions prepared.")
            if not await super().start_service(uri=self.uri):
                return False
        self.service_registries.setdefault(service_name, ClientRegistry())
        return True

    def get_response_buffer(
        self, client_id: ClientId, status: int, result_code: int
    ) -> Optional[PduData]:
        py_pdu_data: PyPduData = self.cls_res_packet()
        py_pdu_data.header.request_id = self.request_id
        py_pdu_data.header.service_name = self.current_service_name
        py_pdu_data.header.client_name = self.current_client_name
        py_pdu_data.header.status = status
        py_pdu_data.header.processing_percentage = 100
        py_pdu_data.header.result_code = result_code
        print(f"[DEBUG] Sending response: {py_pdu_data}")
        return self.res_encoder(py_pdu_data)
    async def poll_request(self) -> Tuple[Optional[str], Event]:
        if self.current_client_name is not None:
            return self.current_service_name, self.SERVER_API_EVENT_NONE
        for service_name, registry in self.service_registries.items():
            for client_name, _handle in registry.clients.items():
                if self.comm_buffer.contains_buffer(service_name, client_name):
                    raw_data = self.comm_buffer.peek_buffer(service_name, client_name)
                    decoder = self.req_decoders.get(service_name, self.req_decoder)
                    request = decoder(raw_data)
                    self.current_client_name = client_name
                    self.current_service_name = service_name
                    self.request_id = request.header.request_id
                    if request.header.opcode == self.CLIENT_API_OPCODE_CANCEL:
                        return service_name, self.SERVER_API_EVENT_REQUEST_CANCEL
                    return service_name, self.SERVER_API_EVENT_REQUEST_IN
        return None, self.SERVER_API_EVENT_NONE

    def get_request(self) -> Tuple[ClientId, PduData]:
        if (
            self.current_service_name
            and self.current_client_name
            and self.comm_buffer.contains_buffer(
                self.current_service_name, self.current_client_name
            )
        ):
            raw_data = self.comm_buffer.get_buffer(
                self.current_service_name, self.current_client_name
            )
            client_handle = self.service_registries[self.current_service_name].clients[
                self.current_client_name
            ]
            return client_handle, raw_data
        raise RuntimeError("No response data available. Call poll_request() first.")

    async def put_response(self, client_id: ClientId, pdu_data: PduData) -> bool:
        client_handle: ClientHandle = client_id
        raw_data = self._build_binary(
            PDU_DATA_RPC_REPLY,
            self.current_service_name,
            client_handle.response_channel_id,
            pdu_data,
        )
        if not await self.comm_service.send_binary(raw_data):
            self.current_client_name = None
            self.current_service_name = None
            self.request_id = None
            return False
        self.current_client_name = None
        self.current_service_name = None
        self.request_id = None
        return True

    async def put_cancel_response(
        self, client_id: ClientId, pdu_data: PduData
    ) -> bool:
        # TODO
        raise NotImplementedError("put_cancel_response is not implemented yet.")
        client_handle: ClientHandle = client_id
        print("Sending cancel response")
        cancel_pdu_raw_data = self.get_response_buffer(
            None, self.API_STATUS_DONE, self.API_RESULT_CODE_CANCELED
        )
        raw_data = self._build_binary(
            PDU_DATA_RPC_REPLY,
            self.current_service_name,
            client_handle.response_channel_id,
            cancel_pdu_raw_data,
        )
        print('before sending cancel response')
        if not await self.comm_service.send_binary(raw_data):
            self.current_client_name = None
            self.current_service_name = None
            self.request_id = None
            return False
        print('after sending cancel response')
        self.current_client_name = None
        self.current_service_name = None
        self.request_id = None
        return True

    def is_server_event_request_in(self, event: Event) -> bool:
        return event == self.SERVER_API_EVENT_REQUEST_IN

    def is_server_event_cancel(self, event: Event) -> bool:
        return event == self.SERVER_API_EVENT_REQUEST_CANCEL

    def is_server_event_none(self, event: Event) -> bool:
        return event == self.SERVER_API_EVENT_NONE


__all__ = ["RemotePduServiceServerManager"]
