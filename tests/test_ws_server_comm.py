import asyncio
import socket

import pytest
import websockets
from websockets.exceptions import ConnectionClosed

from hakoniwa_pdu.impl.communication_buffer import CommunicationBuffer
from hakoniwa_pdu.impl.pdu_channel_config import PduChannelConfig
from hakoniwa_pdu.impl.websocket_server_communication_service import (
    WebSocketServerCommunicationService,
)

pytestmark = pytest.mark.asyncio


def _get_free_port() -> int:
    s = socket.socket()
    s.bind(("localhost", 0))
    port = s.getsockname()[1]
    s.close()
    return port


async def _start_server():
    port = _get_free_port()
    host = "127.0.0.1"
    uri = f"ws://{host}:{port}"
    srv = WebSocketServerCommunicationService(version="v2")
    pdu_config_path = "tests/pdu_config.json"
    buf = CommunicationBuffer(PduChannelConfig(pdu_config_path))
    disconnected: list[str] = []
    srv.on_disconnect = lambda cid: disconnected.append(cid)
    assert await srv.start_service(buf, uri) is True
    return srv, host, port, disconnected


async def test_single_connection_and_legacy_send():
    srv, host, port, disconnected = await _start_server()
    uri = f"ws://{host}:{port}"
    try:
        async with websockets.connect(uri) as ws:
            await asyncio.sleep(0.05)
            assert len(srv.clients) == 1
            cid = next(iter(srv.clients))

            data = b"ping"
            ok = await srv.send_binary(bytearray(data))
            assert ok
            recv = await asyncio.wait_for(ws.recv(), timeout=1.0)
            assert recv == data

            data2 = b"hello"
            ok2 = await srv.send_binary_to(cid, data2)
            assert ok2
            recv2 = await asyncio.wait_for(ws.recv(), timeout=1.0)
            assert recv2 == data2

        await asyncio.sleep(0.05)
        assert disconnected == [cid]
        assert await srv.send_binary_to(cid, b"more") is False
    finally:
        await srv.stop_service()


async def test_unknown_client_id_send_fails():
    srv, *_ = await _start_server()
    try:
        ok = await srv.send_binary_to("ws999999", b"x")
        assert ok is False
    finally:
        await srv.stop_service()


async def test_second_client_is_rejected():
    srv, host, port, *_ = await _start_server()
    uri = f"ws://{host}:{port}"
    try:
        async with websockets.connect(uri) as ws1:
            with pytest.raises(ConnectionClosed):
                async with websockets.connect(uri) as ws2:
                    await ws2.recv()
            await ws1.send(b"ok")
    finally:
        await srv.stop_service()

