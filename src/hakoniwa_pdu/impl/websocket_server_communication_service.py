import asyncio
import inspect
import logging
from dataclasses import dataclass, field
from typing import Callable, Dict, Optional
from urllib.parse import urlparse

import websockets
from websockets.server import WebSocketServerProtocol

from .communication_buffer import CommunicationBuffer
from .websocket_base_communication_service import WebSocketBaseCommunicationService

logger = logging.getLogger(__name__)


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
        self.on_disconnect: Callable[[str], None] = lambda cid: None
        self._id_seq: int = 0

    def _next_client_id(self) -> str:
        self._id_seq += 1
        return f"ws{self._id_seq:06d}"

    def _remove_client_by_id(self, client_id: str) -> None:
        session = self.clients.pop(client_id, None)
        if session and session.websocket is self.websocket:
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
            logger.info(f"WebSocket server started at {parsed.hostname}:{parsed.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to start WebSocket server: {e}")
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
        logger.debug("_client_handler: new client connected")
        if self.websocket is not None:
            # Allow only one client
            await websocket.close()
            return
        self.websocket = websocket
        client_id = self._next_client_id()
        self.clients[client_id] = ClientSession(client_id, websocket)
        original_handler = self.handler
        original_data_handler = getattr(self, "data_handler", None)
        if original_handler is not None:
            async def handler_with_client(packet):
                if inspect.iscoroutinefunction(original_handler):
                    await original_handler(packet, client_id)
                else:
                    await asyncio.to_thread(original_handler, packet, client_id)
            self.handler = handler_with_client

        if original_data_handler is not None:
            async def data_handler_with_client(packet):
                if inspect.iscoroutinefunction(original_data_handler):
                    await original_data_handler(packet, client_id)
                else:
                    await asyncio.to_thread(original_data_handler, packet, client_id)
            self.data_handler = data_handler_with_client
        try:
            if self.version == "v1":
                await self._receive_loop_v1(websocket)
            else:
                await self._receive_loop_v2(websocket)
        finally:
            if original_handler is not None:
                self.handler = original_handler
            if original_data_handler is not None:
                self.data_handler = original_data_handler
            self._remove_client_by_id(client_id)
            try:
                self.on_disconnect(client_id)
            except Exception:
                pass

    async def send_binary_to(
        self, client_id: str, raw_data: bytes | bytearray
    ) -> bool:
        session = self.clients.get(client_id)
        if session is None:
            return False
        async with session.send_lock:
            try:
                await session.websocket.send(raw_data)
                return True
            except Exception as e:
                logger.error(f"Failed to send binary to {client_id}: {e}")
                try:
                    await session.websocket.close()
                except Exception:
                    pass
                self._remove_client_by_id(client_id)
                try:
                    self.on_disconnect(client_id)
                except Exception:
                    pass
                return False

    async def send_data_to(
        self, client_id: str, robot_name: str, channel_id: int, pdu_data: bytearray
    ) -> bool:
        raw = self._pack_pdu(robot_name, channel_id, pdu_data)
        return await self.send_binary_to(client_id, raw)

    async def send_data(
        self, robot_name: str, channel_id: int, pdu_data: bytearray
    ) -> bool:
        if not self.clients:
            logger.warning("WebSocket not connected")
            return False
        client_id = next(iter(self.clients))
        return await self.send_data_to(client_id, robot_name, channel_id, pdu_data)

    async def send_binary(self, raw_data: bytearray) -> bool:
        if not self.clients:
            logger.warning("WebSocket not connected")
            return False
        client_id = next(iter(self.clients))
        return await self.send_binary_to(client_id, raw_data)