import asyncio
import threading
import websockets

from .data_packet import DataPacket
from .communication_buffer import CommunicationBuffer
from .icommunication_service import ICommunicationService


class WebSocketCommunicationService(ICommunicationService):
    def __init__(self):
        self.websocket = None
        self.uri = ""
        self.service_enabled = False
        self.comm_buffer = None
        self._loop = None
        self._recv_task = None
        self._thread = None

    def start_service(self, comm_buffer: CommunicationBuffer, uri: str = "") -> bool:
        self.comm_buffer = comm_buffer
        self.uri = uri

        def run_loop():
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            self._loop.run_until_complete(self._connect())

        self._thread = threading.Thread(target=run_loop, daemon=True)
        self._thread.start()
        return True

    def stop_service(self) -> bool:
        self.service_enabled = False
        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)
        return True

    def is_service_enabled(self) -> bool:
        return self.service_enabled

    def get_server_uri(self) -> str:
        return self.uri

    def send_data(self, robot_name: str, channel_id: int, pdu_data: bytearray) -> bool:
        if not self.service_enabled or not self.websocket:
            print("[WARN] WebSocket not connected")
            return False

        packet = DataPacket(robot_name, channel_id, pdu_data)
        encoded = packet.encode()
        asyncio.run_coroutine_threadsafe(
            self.websocket.send(encoded), self._loop
        )
        return True

    async def _connect(self):
        try:
            async with websockets.connect(self.uri) as ws:
                print("[INFO] WebSocket connected.")
                self.websocket = ws
                self.service_enabled = True
                await self._receive_loop()
        except Exception as e:
            print(f"[ERROR] WebSocket connection failed: {e}")
        finally:
            self.service_enabled = False

    async def _receive_loop(self):
        async for message in self.websocket:
            if isinstance(message, bytes):
                packet = DataPacket.decode(bytearray(message))
                if packet and self.comm_buffer:
                    self.comm_buffer.put_packet(packet)
            else:
                print(f"[WARN] Unexpected message type: {type(message)}")
