from dataclasses import dataclass
from typing import Dict, Optional, Tuple, Callable
import asyncio
import logging

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

logger = logging.getLogger(__name__)


@dataclass
class ClientHandle:
    """Handle information for a registered RPC client."""

    client_id: int
    request_channel_id: int
    response_channel_id: int
    transport_client_id: str


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
        self._declared_read: dict[str, set[tuple[str, int]]] = {}
        self._read_index: dict[tuple[str, int], set[str]] = {}
        comm_service.register_event_handler(self.handler)
        if hasattr(comm_service, "register_data_event_handler"):
            comm_service.register_data_event_handler(self._on_pdu_data)
        comm_service.on_disconnect = self.on_disconnect
        self._pdu_data_handler: Optional[Callable[[str, DataPacket], None]] = None
        self.topic_service_started = False
        self.rpc_service_started = False

    async def _handler_register_client(
        self, packet: DataPacket, transport_client_id: str
    ) -> None:
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
            transport_client_id=transport_client_id,
        )
        registry.clients[body_pdu_data.header.client_name] = client_handle

        logger.debug(f"Registered RPC client: {body_pdu_data.header.client_name}")
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
        logger.debug(
            f"Sent register client response: {body_pdu_data.header.client_name}"
        )

    def register_handler_pdu_for_read(self, handler: Callable) -> None:
        self.pdu_for_read_handler = handler
    def register_handler_pdu_for_write(self, handler: Callable) -> None:
        self.pdu_for_write_handler = handler
    def register_handler_request_pdu_read(self, handler: Callable[[str, DataPacket], None]) -> None:
        """Register handler for REQUEST_PDU_READ packets.

        The handler receives ``(client_id, packet)`` arguments.
        """
        self.request_pdu_read_handler = handler

    async def handler(self, packet: DataPacket, client_id: str) -> None:
        if packet.meta_pdu.meta_request_type == DECLARE_PDU_FOR_READ:
            robot = packet.meta_pdu.robot_name
            ch = packet.meta_pdu.channel_id
            key = (robot, ch)

            s = self._declared_read.setdefault(client_id, set())
            if key not in s:
                s.add(key)
                idx = self._read_index.setdefault(key, set())
                idx.add(client_id)
                logger.debug(
                    f"declared_for_read: client={client_id} ({robot}, {ch})"
                )
            if self.pdu_for_read_handler is not None:
                self.pdu_for_read_handler(client_id, packet)
            return
        elif packet.meta_pdu.meta_request_type == DECLARE_PDU_FOR_WRITE:
            logger.info(
                f"Declare PDU for write: {packet.robot_name}, channel_id={packet.channel_id}"
            )
            if self.pdu_for_write_handler is not None:
                self.pdu_for_write_handler(packet)
        elif packet.meta_pdu.meta_request_type == REQUEST_PDU_READ:
            robot = packet.meta_pdu.robot_name
            ch = packet.meta_pdu.channel_id
            if self.request_pdu_read_handler is not None:
                self.request_pdu_read_handler(client_id, packet)
            else:
                logger.debug(
                    f"REQUEST_PDU_READ: no handler; client={client_id} ({robot},{ch})"
                )
            return
        elif packet.meta_pdu.meta_request_type == REGISTER_RPC_CLIENT:
            logger.info(
                f"Register RPC client: {packet.robot_name}, channel_id={packet.channel_id}"
            )
            await self._handler_register_client(packet, client_id)
        else:
            raise NotImplementedError("Unknown packet type")

    def register_handler_pdu_data(self, handler: Callable[[str, DataPacket], None]) -> None:
        """Called for every PDU_DATA after buffering. Handler receives (client_id, packet)."""
        self._pdu_data_handler = handler

    async def _on_pdu_data(self, packet: DataPacket, client_id: str):
        if self._pdu_data_handler is not None:
            try:
                self._pdu_data_handler(client_id, packet)
            except Exception as e:
                logger.warning(f"pdu_data_handler raised: {e}")

    def on_disconnect(self, client_id: str):
        topics = self._declared_read.pop(client_id, None)
        if topics:
            for key in topics:
                idx = self._read_index.get(key)
                if idx:
                    idx.discard(client_id)
                    if not idx:
                        self._read_index.pop(key, None)
            logger.debug(f"removed declarations for client={client_id}")
        for svc, registry in list(self.service_registries.items()):
            for cname, handle in list(registry.clients.items()):
                if getattr(handle, "transport_client_id", None) == client_id:
                    registry.clients.pop(cname, None)
                    logger.debug(
                        f"removed RPC client '{cname}' from service '{svc}' on disconnect"
                    )

    async def send_pdu_to(
        self,
        client_id: str,
        robot_name: str,
        channel_id: int,
        pdu_data: bytes | bytearray,
    ) -> bool:
        """Send PDU data only to the specified client."""
        try:
            return await self.comm_service.send_data_to(
                client_id, robot_name, channel_id, bytearray(pdu_data)
            )
        except Exception as e:
            logger.error(
                f"send_pdu_to: failed to send to {client_id} ({robot_name},{channel_id}): {e}"
            )
            return False

    async def reply_latest_to(
        self, client_id: str, robot_name: str, channel_id: int
    ) -> bool:
        """Send the latest buffered data for the given topic to the requester."""
        if not self.comm_buffer:
            logger.debug(
                f"reply_latest_to: no buffer for ({robot_name},{channel_id})"
            )
            return False
        pdu_name = self.comm_buffer.get_pdu_name(robot_name, channel_id)
        if pdu_name is None or not self.comm_buffer.contains_buffer(robot_name, pdu_name):
            logger.debug(
                f"reply_latest_to: no buffer for ({robot_name},{channel_id})"
            )
            return False
        data = self.comm_buffer.get_buffer(robot_name, pdu_name)
        return await self.send_pdu_to(client_id, robot_name, channel_id, data)

    async def publish_pdu(
        self, robot_name: str, channel_id: int, pdu_data: bytes | bytearray
    ) -> int:
        """Send PDU data to all clients declared for the given topic.

        Returns the number of successful transmissions."""
        key = (robot_name, channel_id)
        cids = list(self._read_index.get(key, set()))
        if not cids:
            logger.debug(
                f"publish_pdu: no subscribers for ({robot_name}, {channel_id})"
            )
            return 0

        sent = 0
        for cid in cids:
            try:
                ok = await self.comm_service.send_data_to(
                    cid, robot_name, channel_id, bytearray(pdu_data)
                )
                if ok:
                    sent += 1
                else:
                    logger.warning(
                        f"publish_pdu: failed to send to {cid} ({robot_name},{channel_id})"
                    )
            except Exception as e:
                logger.error(
                    f"publish_pdu: exception sending to {cid}: {e}"
                )
        return sent

    async def start_topic_service(self) -> bool:
        if self.rpc_service_started:
            raise RuntimeError("Cannot start topic service after RPC service has started")
        
        offmap = offset_map.create_offmap(self.offset_path)
        self.service_config = ServiceConfig(
            self.service_config_path, offmap, hakopy=None
        )
        pdudef = self.service_config.append_pdu_def(self.pdu_config.get_pdudef())
        self.pdu_config.update_pdudef(pdudef)
        logger.info("Service PDU definitions prepared.")
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
            logger.info("Service PDU definitions prepared.")
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
        logger.debug(f"Sending response: {py_pdu_data}")
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
        send_ok = False
        if hasattr(self.comm_service, "send_binary_to") and client_handle.transport_client_id:
            send_ok = await self.comm_service.send_binary_to(
                client_handle.transport_client_id, raw_data
            )
        else:
            send_ok = await self.comm_service.send_binary(raw_data)
        if not send_ok:
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
        logger.info("Sending cancel response")
        cancel_pdu_raw_data = self.get_response_buffer(
            None, self.API_STATUS_DONE, self.API_RESULT_CODE_CANCELED
        )
        raw_data = self._build_binary(
            PDU_DATA_RPC_REPLY,
            self.current_service_name,
            client_handle.response_channel_id,
            cancel_pdu_raw_data,
        )
        logger.debug('before sending cancel response')
        if not await self.comm_service.send_binary(raw_data):
            self.current_client_name = None
            self.current_service_name = None
            self.request_id = None
            return False
        logger.debug('after sending cancel response')
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