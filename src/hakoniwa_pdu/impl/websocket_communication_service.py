import asyncio
import websockets
from typing import Optional
from .data_packet import DataPacket
from .communication_buffer import CommunicationBuffer
from .icommunication_service import ICommunicationService
from .pdu_channel_config import PduChannelConfig
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
from hakoniwa_pdu.pdu_msgs.hako_srv_msgs.pdu_pytype_ServiceRequestHeader import ServiceRequestHeader
from hakoniwa_pdu.pdu_msgs.hako_srv_msgs.pdu_pytype_ServiceResponseHeader import ServiceResponseHeader
from hakoniwa_pdu.pdu_msgs.hako_srv_msgs.pdu_conv_ServiceRequestHeader import pdu_to_py_ServiceRequestHeader
from hakoniwa_pdu.pdu_msgs.hako_srv_msgs.pdu_conv_ServiceResponseHeader import pdu_to_py_ServiceResponseHeader

class WebSocketCommunicationService(ICommunicationService):
    def __init__(self, version: str = "v1"):
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.uri: str = ""
        self.service_enabled: bool = False
        self.comm_buffer: Optional[CommunicationBuffer] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._receive_task: Optional[asyncio.Task] = None
        self.version = version
        self.handler = None

    def set_channel_config(self, config: PduChannelConfig):
        """Set the PDU channel configuration."""
        self.config = config

    async def start_service(self, comm_buffer: CommunicationBuffer, uri: str = "", polling_interval: float = 0.02) -> bool:
        self.comm_buffer = comm_buffer
        self.uri = uri
        self.polling_interval = polling_interval
        self._loop = asyncio.get_event_loop()

        try:
            self.websocket = await websockets.connect(self.uri)
            self.service_enabled = True
            if self.version == "v1":
                self._receive_task = asyncio.create_task(self._receive_loop_v1())
            else:
                self._receive_task = asyncio.create_task(self._receive_loop_v2())
            print("[INFO] WebSocket connected and receive loop started")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to connect WebSocket: {e}")
            self.service_enabled = False
            return False

    async def stop_service(self) -> bool:
        self.service_enabled = False

        if self._receive_task:
            self._receive_task.cancel()
            try:
                await self._receive_task
            except asyncio.CancelledError:
                pass

        if self.websocket:
            try:
                await self.websocket.close()
                print("[INFO] WebSocket closed")
            except Exception as e:
                print(f"[ERROR] Error closing WebSocket: {e}")

        self.websocket = None
        self._receive_task = None
        return True

    def start_service_nowait(self, comm_buffer: CommunicationBuffer, uri: str = "") -> bool:
        return False  # Not implemented for WebSocket
    def stop_service_nowait(self) -> bool:
        return False  # Not implemented for WebSocket
    def run_nowait(self) -> bool:
        return False  # Not implemented for WebSocket
    def send_data_nowait(self, robot_name: str, channel_id: int, pdu_data: bytearray) -> bool:
        return False # Not implemented for WebSocket

    def is_service_enabled(self) -> bool:
        return self.service_enabled and self.websocket is not None

    def get_server_uri(self) -> str:
        return self.uri

    async def send_data(self, robot_name: str, channel_id: int, pdu_data: bytearray) -> bool:
        if not self.service_enabled or not self.websocket:
            print("[WARN] WebSocket not connected")
            return False

        try:
            packet = DataPacket(robot_name, channel_id, pdu_data)
            encoded = packet.encode()
            await self.websocket.send(encoded)
            return True
        except Exception as e:
            print(f"[ERROR] Failed to send data: {e}")
            return False

    async def send_binary(self, raw_data: bytearray) -> bool:
        if not self.service_enabled or not self.websocket:
            print("[WARN] WebSocket not connected")
            return False

        try:
            await self.websocket.send(raw_data)
            return True
        except Exception as e:
            print(f"[ERROR] Failed to send binary data: {e}")
            return False

    async def _receive_loop_v1(self):
        try:
            async for message in self.websocket:
                if isinstance(message, bytes):
                    packet = DataPacket.decode(bytearray(message))
                    if packet and self.comm_buffer:
                        self.comm_buffer.put_packet(packet)
                else:
                    print(f"[WARN] Unexpected message type: {type(message)}")
        except asyncio.CancelledError:
            print("[INFO] Receive loop cancelled")
        except Exception as e:
            print(f"[ERROR] Receive loop failed: {e}")


    async def _receive_loop_v2(self):
        try:
            async for message in self.websocket:
                if isinstance(message, bytes):
                    packet = DataPacket.decode(bytearray(message), version=self.version)
                    if packet and self.comm_buffer and packet.meta_pdu.message_type in [PDU_DATA]:
                        self.comm_buffer.put_packet(packet)
                    elif packet and packet.meta_pdu.message_type in [PDU_DATA_RPC_REQUEST]:
                        header: ServiceRequestHeader = pdu_to_py_ServiceRequestHeader(packet.get_pdu_data())
                        self.comm_buffer.put_rpc_packet(header.service_name, header.client_name, packet.get_pdu_data())
                    elif packet and packet.meta_pdu.message_type in [PDU_DATA_RPC_REPLY]:
                        header: ServiceResponseHeader = pdu_to_py_ServiceResponseHeader(packet.get_pdu_data())
                        self.comm_buffer.put_rpc_packet(header.service_name, header.client_name, packet.get_pdu_data())
                    elif packet and packet.meta_pdu.message_type in [DECLARE_PDU_FOR_READ, DECLARE_PDU_FOR_WRITE, REGISTER_RPC_CLIENT] and self.handler:
                        self.handler(packet)
                    else:
                        raise ValueError(f"Unknown message type: {packet.meta_pdu.message_type if packet else 'None'}")
                else:
                    print(f"[WARN] Unexpected message type: {type(message)}")
        except asyncio.CancelledError:
            print("[INFO] Receive loop cancelled")
        except Exception as e:
            print(f"[ERROR] Receive loop failed: {e}")

    def register_event_handler(self, handler: callable):
        self.handler = handler