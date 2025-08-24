import asyncio
from dataclasses import dataclass, field
from typing import Dict, Optional
from urllib.parse import urlparse

import websockets
from websockets.server import WebSocketServerProtocol

from .communication_buffer import CommunicationBuffer
from .websocket_base_communication_service import WebSocketBaseCommunicationService


@dataclass
class ClientSession:
    """Session information for a connected WebSocket client."""

    client_id: str
    websocket: WebSocketServerProtocol
    name: Optional[str] = None
    send_lock: asyncio.Lock = field(default_factory=asyncio.Lock)


class WebSocketServerCommunicationService(WebSocketBaseCommunicationService):
    """WebSocketベースのサーバ通信サービス."""

    def __init__(self, version: str = "v1"):
        super().__init__(version)
        self.server: Optional[websockets.server.Serve] = None
        # Store active client sessions; still single-client by default
        self.clients: Dict[str, ClientSession] = {}

    def _remove_client(self, websocket: WebSocketServerProtocol) -> None:
        """Remove client session associated with ``websocket``."""
        client_id = f"client_{id(websocket)}"
        self.clients.pop(client_id, None)
        if self.websocket is websocket:
            self.websocket = None

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

    async def _client_handler(
        self, websocket: WebSocketServerProtocol, path: str | None = None
    ):
        """Handle a newly connected client.

        Recent versions of the ``websockets`` package (>=11) invoke the
        connection handler with only the websocket argument, while older
        versions pass an additional ``path`` parameter.  To remain
        compatible across versions we accept ``path`` as an optional
        argument and ignore it.
        """
        print("[DEBUG] _client_handler: new client connected")
        if self.websocket is not None:
            # Allow only one client
            await websocket.close()
            return
        self.websocket = websocket
        client_id = f"client_{id(websocket)}"
        self.clients[client_id] = ClientSession(client_id, websocket)
        try:
            if self.version == "v1":
                await self._receive_loop_v1(websocket)
            else:
                await self._receive_loop_v2(websocket)
        finally:
            self._remove_client(websocket)

    async def send_data(
        self, robot_name: str, channel_id: int, pdu_data: bytearray
    ) -> bool:
        success = await super().send_data(robot_name, channel_id, pdu_data)
        if not success and self.websocket and self.websocket.closed:
            self._remove_client(self.websocket)
        return success

    async def send_binary(self, raw_data: bytearray) -> bool:
        success = await super().send_binary(raw_data)
        if not success and self.websocket and self.websocket.closed:
            self._remove_client(self.websocket)
        return success

