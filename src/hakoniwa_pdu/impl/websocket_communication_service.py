import asyncio
import websockets
from typing import Optional

from .communication_buffer import CommunicationBuffer
from .pdu_channel_config import PduChannelConfig
from .websocket_base_communication_service import WebSocketBaseCommunicationService


class WebSocketCommunicationService(WebSocketBaseCommunicationService):
    def __init__(self, version: str = "v1"):
        print(f"[INFO] WebSocketCommunicationService created with version: {version}")
        super().__init__(version)

    async def start_service(
        self, comm_buffer: CommunicationBuffer, uri: str = "", polling_interval: float = 0.02
    ) -> bool:
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

