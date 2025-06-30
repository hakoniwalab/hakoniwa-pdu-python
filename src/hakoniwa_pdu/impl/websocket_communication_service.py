import asyncio
import websockets
from typing import Optional
from .data_packet import DataPacket
from .communication_buffer import CommunicationBuffer
from .icommunication_service import ICommunicationService


class WebSocketCommunicationService(ICommunicationService):
    def __init__(self):
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.uri: str = ""
        self.service_enabled: bool = False
        self.comm_buffer: Optional[CommunicationBuffer] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._receive_task: Optional[asyncio.Task] = None

    async def start_service(self, comm_buffer: CommunicationBuffer, uri: str = "") -> bool:
        self.comm_buffer = comm_buffer
        self.uri = uri
        self._loop = asyncio.get_event_loop()

        try:
            self.websocket = await websockets.connect(self.uri)
            self.service_enabled = True
            self._receive_task = asyncio.create_task(self._receive_loop())
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

    async def _receive_loop(self):
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