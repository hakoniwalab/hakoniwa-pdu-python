import asyncio
import socket
import pytest
from hakoniwa_pdu.impl.communication_buffer import CommunicationBuffer
from hakoniwa_pdu.impl.pdu_channel_config import PduChannelConfig
from hakoniwa_pdu.impl.websocket_server_communication_service import WebSocketServerCommunicationService
from hakoniwa_pdu.impl.websocket_communication_service import WebSocketCommunicationService
from hakoniwa_pdu.impl.data_packet import DataPacket, DECLARE_PDU_FOR_READ
from hakoniwa_pdu.rpc.remote.remote_pdu_service_server_manager import RemotePduServiceServerManager

pytestmark = pytest.mark.asyncio


def _get_free_port() -> int:
    s = socket.socket()
    s.bind(("localhost", 0))
    port = s.getsockname()[1]
    s.close()
    return port


async def test_declare_registry_and_cleanup():
    port = _get_free_port()
    uri = f"ws://127.0.0.1:{port}"
    pdu_config_path = "tests/pdu_config.json"
    offset_path = "tests/config/offset"
    pdu_channel_config = PduChannelConfig(pdu_config_path)

    server_comm = WebSocketServerCommunicationService(version="v2")
    server_mgr = RemotePduServiceServerManager("srv", pdu_config_path, offset_path, server_comm, uri)
    server_buf = CommunicationBuffer(pdu_channel_config)
    assert await server_comm.start_service(server_buf, uri) is True

    client_comm = WebSocketCommunicationService(version="v2")
    client_buf = CommunicationBuffer(pdu_channel_config)
    assert await client_comm.start_service(client_buf, uri) is True
    await asyncio.sleep(0.1)

    cid = next(iter(server_comm.clients))
    pkt = DataPacket("robot", 1, bytearray())
    encoded = pkt.encode("v2", meta_request_type=DECLARE_PDU_FOR_READ)
    await client_comm.send_binary(encoded)
    await asyncio.sleep(0.1)

    assert ("robot", 1) in server_mgr._declared_read.get(cid, set())
    assert cid in server_mgr._read_index.get(("robot", 1), set())

    await client_comm.stop_service()
    await asyncio.sleep(0.1)
    assert cid not in server_mgr._declared_read
    assert cid not in server_mgr._read_index.get(("robot", 1), set())

    await server_comm.stop_service()
