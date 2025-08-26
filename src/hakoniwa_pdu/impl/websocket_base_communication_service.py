import asyncio
import inspect
import logging
from typing import Optional, Callable, Union, Awaitable
from websockets import WebSocketClientProtocol, WebSocketServerProtocol

from .communication_buffer import CommunicationBuffer
from .data_packet import DataPacket, PDU_DATA, PDU_DATA_RPC_REQUEST, PDU_DATA_RPC_REPLY, DECLARE_PDU_FOR_READ, DECLARE_PDU_FOR_WRITE, REQUEST_PDU_READ, REGISTER_RPC_CLIENT
from .icommunication_service import ICommunicationService
from .pdu_channel_config import PduChannelConfig
from hakoniwa_pdu.pdu_msgs.hako_srv_msgs.pdu_pytype_ServiceRequestHeader import (
    ServiceRequestHeader,
)
from hakoniwa_pdu.pdu_msgs.hako_srv_msgs.pdu_pytype_ServiceResponseHeader import (
    ServiceResponseHeader,
)
from hakoniwa_pdu.pdu_msgs.hako_srv_msgs.pdu_conv_ServiceRequestHeader import (
    pdu_to_py_ServiceRequestHeader,
)
from hakoniwa_pdu.pdu_msgs.hako_srv_msgs.pdu_conv_ServiceResponseHeader import (
    pdu_to_py_ServiceResponseHeader,
)

logger = logging.getLogger(__name__)


class WebSocketBaseCommunicationService(ICommunicationService):
    def __init__(self, version: str = "v1"):
        logger.info(f"WebSocketBaseCommunicationService created with version: {version}")
        self.websocket: Optional[
            Union[WebSocketClientProtocol, WebSocketServerProtocol]
        ] = None
        self.uri: str = ""
        self.service_enabled: bool = False
        self.comm_buffer: Optional[CommunicationBuffer] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._receive_task: Optional[asyncio.Task] = None
        self.version = version
        #self.handler: Optional[Callable] = None
        self.handler: Optional[Callable[[DataPacket], Awaitable[None]]] = None
        # Called on every PDU_DATA after it is buffered
        self.data_handler: Optional[Callable[[DataPacket], Awaitable[None]]] = None

    def set_channel_config(self, config: PduChannelConfig):
        self.config = config

    def start_service_nowait(self, comm_buffer: CommunicationBuffer, uri: str = "") -> bool:
        return False

    def stop_service_nowait(self) -> bool:
        return False

    def run_nowait(self) -> bool:
        return False

    def send_data_nowait(self, robot_name: str, channel_id: int, pdu_data: bytearray) -> bool:
        return False

    def is_service_enabled(self) -> bool:
        return self.service_enabled and self.websocket is not None

    def get_server_uri(self) -> str:
        return self.uri

    def _pack_pdu(
        self, robot_name: str, channel_id: int, pdu_data: bytearray
    ) -> bytearray:
        """Pack PDU data into wire format."""
        packet = DataPacket(robot_name, channel_id, pdu_data)
        return packet.encode(self.version, meta_request_type=PDU_DATA)

    async def send_data(self, robot_name: str, channel_id: int, pdu_data: bytearray) -> bool:
        if not self.service_enabled or not self.websocket:
            logger.warning("WebSocket not connected")
            return False
        try:
            encoded = self._pack_pdu(robot_name, channel_id, pdu_data)
            await self.websocket.send(encoded)
            return True
        except Exception as e:
            logger.error(f"Failed to send data: {e}")
            return False

    async def send_binary(self, raw_data: bytearray) -> bool:
        logger.debug(f"send_binary: sending {len(raw_data)} bytes")
        if not self.service_enabled or not self.websocket:
            logger.warning("WebSocket not connected")
            return False
        try:
            await self.websocket.send(raw_data)
            return True
        except Exception as e:
            logger.error(f"Failed to send binary data: {e}")
            return False

    async def _receive_loop_v1(
        self,
        websocket: Optional[Union[WebSocketClientProtocol, WebSocketServerProtocol]] = None,
    ):
        ws = websocket or self.websocket
        try:
            async for message in ws:
                if isinstance(message, bytes):
                    packet = DataPacket.decode(bytearray(message))
                    if packet and self.comm_buffer:
                        self.comm_buffer.put_packet(packet)
                else:
                    logger.warning(f"Unexpected message type: {type(message)}")
        except asyncio.CancelledError:
            logger.info("Receive loop cancelled")
        except Exception as e:
            logger.error(f"Receive loop failed: {e}")

    async def _receive_loop_v2(
        self,
        websocket: Optional[Union[WebSocketClientProtocol, WebSocketServerProtocol]] = None,
    ):
        ws = websocket or self.websocket
        logger.debug("_receive_loop_v2: starting")
        try:
            async for message in ws:
                logger.debug(f"_receive_loop_v2: received message")
                if isinstance(message, bytes):
                    packet = DataPacket.decode(bytearray(message), version=self.version)
                    if packet and self.comm_buffer and packet.meta_pdu.meta_request_type in [PDU_DATA]:
                        self.comm_buffer.put_packet(packet)
                        if self.data_handler is not None:
                            try:
                                if inspect.iscoroutinefunction(self.data_handler):
                                    asyncio.create_task(self.data_handler(packet))
                                else:
                                    asyncio.create_task(asyncio.to_thread(self.data_handler, packet))
                            except Exception as e:
                                logger.error(f"scheduling data_handler failed: {e}")
                        continue
                    elif packet and packet.meta_pdu.meta_request_type in [PDU_DATA_RPC_REQUEST]:
                        logger.debug(f'handling RPC request: meta={packet.meta_pdu.robot_name}')
                        header: ServiceRequestHeader = pdu_to_py_ServiceRequestHeader(
                            packet.get_pdu_data()
                        )
                        logger.debug(f"handling RPC request service_name={header.service_name}, client_name={header.client_name}")
                        self.comm_buffer.put_rpc_packet(
                            header.service_name, header.client_name, packet.get_pdu_data()
                        )
                    elif packet and packet.meta_pdu.meta_request_type in [PDU_DATA_RPC_REPLY]:
                        header: ServiceResponseHeader = pdu_to_py_ServiceResponseHeader(
                            packet.get_pdu_data()
                        )
                        self.comm_buffer.put_rpc_packet(
                            header.service_name, header.client_name, packet.get_pdu_data()
                        )
                    elif (
                        packet
                        and packet.meta_pdu.meta_request_type
                        in [DECLARE_PDU_FOR_READ, DECLARE_PDU_FOR_WRITE, REQUEST_PDU_READ, REGISTER_RPC_CLIENT]
                    ):
                        logger.debug(f"handling packet {packet.meta_pdu.meta_request_type}")
                        if self.handler is None:
                            raise RuntimeError("handler not registered")
                        # 受信ループをブロックしない：コルーチンなら create_task、同期関数なら to_thread
                        try:
                            if inspect.iscoroutinefunction(self.handler):
                                asyncio.create_task(self.handler(packet))
                            else:
                                asyncio.create_task(asyncio.to_thread(self.handler, packet))
                            logger.debug("handler scheduled")
                        except Exception as e:
                            logger.error(f"scheduling handler failed: {e}")
                    else:
                        raise ValueError(
                            f"Unknown message type: {packet.meta_pdu.meta_request_type if packet else 'None'}"
                        )
                else:
                    logger.warning(f"Unexpected message type: {type(message)}")
                logger.debug("message processed")
        except asyncio.CancelledError:
            logger.info("Receive loop cancelled")
        except Exception as e:
            logger.error(f"Receive loop failed: {e}")
        logger.debug("_receive_loop_v2: ending")

    def register_event_handler(self, handler: Callable[[DataPacket], Awaitable[None]]):
        self.handler = handler

    def register_data_event_handler(self, handler: Callable[[DataPacket], Awaitable[None]]):
        """Called for every PDU_DATA after it is buffered."""
        self.data_handler = handler