import asyncio
from typing import Optional
from urllib.parse import urlparse

import websockets
from websockets.server import WebSocketServerProtocol

from .communication_buffer import CommunicationBuffer
from .websocket_base_communication_service import WebSocketBaseCommunicationService


class WebSocketServerCommunicationService(WebSocketBaseCommunicationService):
    """WebSocketベースのサーバ通信サービス."""

    def __init__(self, version: str = "v1"):
        super().__init__(version)
        self.server: Optional[websockets.server.Serve] = None

    async def start_service(
        self,
        comm_buffer: CommunicationBuffer,
        uri: str = "",
        polling_interval: float = 0.02,
    ) -> bool:
        """Start WebSocket server."""
        self.comm_buffer = comm_buffer
        self.uri = uri
        self.polling_interval = polling_interval
        self._loop = asyncio.get_event_loop()
        parsed = urlparse(uri)
        try:
            self.server = await websockets.serve(self._client_handler, parsed.hostname, parsed.port)
            self.service_enabled = True
            print(f"[INFO] WebSocket server started at {parsed.hostname}:{parsed.port}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to start WebSocket server: {e}")
            self.service_enabled = False
            return False

    async def stop_service(self) -> bool:
        self.service_enabled = False
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.server = None
        if self.websocket:
            try:
                await self.websocket.close()
            except Exception:
                pass
            self.websocket = None
        return True

    async def _client_handler(self, websocket: WebSocketServerProtocol, path: str):
        print(f"[DEBUG] _client_handler: new client connected")
        if self.websocket is not None:
            # Allow only one client
            await websocket.close()
            return
        self.websocket = websocket
        try:
            if self.version == "v1":
                await self._receive_loop_v1(websocket)
            else:
                await self._receive_loop_v2(websocket)
        finally:
            self.websocket = None

