import asyncio
import socket
import pytest

from hakoniwa_pdu.impl.websocket_server_communication_service import WebSocketServerCommunicationService
from hakoniwa_pdu.impl.websocket_communication_service import WebSocketCommunicationService
from hakoniwa_pdu.impl.pdu_channel_config import PduChannelConfig
from hakoniwa_pdu.impl.communication_buffer import CommunicationBuffer
from hakoniwa_pdu.rpc.remote.remote_pdu_service_server_manager import RemotePduServiceServerManager
from hakoniwa_pdu.rpc.remote.remote_pdu_service_client_manager import RemotePduServiceClientManager

@pytest.mark.asyncio
async def test_server_pdu_data_event():
    def _get_free_port():
        s = socket.socket()
        s.bind(("localhost", 0))
        port = s.getsockname()[1]
        s.close()
        return port

    port = _get_free_port()
    uri = f"ws://localhost:{port}"
    pdu_config_path = "tests/pdu_config.json"
    offset_path = "tests/config/offset"

    server_comm = WebSocketServerCommunicationService(version="v2")
    server_manager = RemotePduServiceServerManager("srv", pdu_config_path, offset_path, server_comm, uri)
    record = []
    server_manager.register_handler_pdu_data(lambda cid, pkt: record.append((cid, pkt)))

    assert await server_manager.start_service(uri)
    client_comm = WebSocketCommunicationService(version="v2")
    client_buffer = CommunicationBuffer(PduChannelConfig(pdu_config_path))
    assert await client_comm.start_service(client_buffer, uri)
    await asyncio.sleep(0.1)

    data = b"hello"
    await client_comm.send_data("test_client", 1, data)
    await asyncio.sleep(0.1)

    assert len(record) == 1
    cid, pkt = record[0]
    assert pkt.get_robot_name() == "test_client"
    assert server_manager.comm_buffer.get_buffer("test_client", "client_to_server") == data

    await client_comm.stop_service()
    await server_manager.stop_service()

@pytest.mark.asyncio
async def test_client_pdu_data_event():
    def _get_free_port():
        s = socket.socket()
        s.bind(("localhost", 0))
        port = s.getsockname()[1]
        s.close()
        return port

    port = _get_free_port()
    uri = f"ws://localhost:{port}"
    pdu_config_path = "tests/pdu_config.json"
    offset_path = "tests/config/offset"

    server_comm = WebSocketServerCommunicationService(version="v2")
    server_buffer = CommunicationBuffer(PduChannelConfig(pdu_config_path))
    assert await server_comm.start_service(server_buffer, uri)

    client_comm = WebSocketCommunicationService(version="v2")
    client_manager = RemotePduServiceClientManager("cli", pdu_config_path, offset_path, client_comm, uri)
    record = []
    client_manager.register_handler_pdu_data(lambda pkt: record.append(pkt))
    assert await client_manager.start_service(uri)
    await asyncio.sleep(0.1)

    data = b"world"
    await server_comm.send_data("test_server", 2, data)
    await asyncio.sleep(0.1)

    assert len(record) == 1
    pkt = record[0]
    assert pkt.get_robot_name() == "test_server"
    assert client_manager.comm_buffer.get_buffer("test_server", "server_to_client") == data

    await client_manager.stop_service()
    await server_comm.stop_service()

@pytest.mark.asyncio
async def test_pdu_data_no_handler():
    def _get_free_port():
        s = socket.socket()
        s.bind(("localhost", 0))
        port = s.getsockname()[1]
        s.close()
        return port

    port = _get_free_port()
    uri = f"ws://localhost:{port}"
    pdu_config_path = "tests/pdu_config.json"
    offset_path = "tests/config/offset"

    server_comm = WebSocketServerCommunicationService(version="v2")
    server_manager = RemotePduServiceServerManager("srv", pdu_config_path, offset_path, server_comm, uri)
    assert await server_manager.start_service(uri)

    client_comm = WebSocketCommunicationService(version="v2")
    client_buffer = CommunicationBuffer(PduChannelConfig(pdu_config_path))
    assert await client_comm.start_service(client_buffer, uri)
    await asyncio.sleep(0.1)

    data = b"x"
    await client_comm.send_data("test_client", 1, data)
    await asyncio.sleep(0.1)

    assert server_manager.comm_buffer.get_buffer("test_client", "client_to_server") == data

    await client_comm.stop_service()
    await server_manager.stop_service()

@pytest.mark.asyncio
async def test_pdu_data_handler_exception():
    def _get_free_port():
        s = socket.socket()
        s.bind(("localhost", 0))
        port = s.getsockname()[1]
        s.close()
        return port

    port = _get_free_port()
    uri = f"ws://localhost:{port}"
    pdu_config_path = "tests/pdu_config.json"
    offset_path = "tests/config/offset"

    server_comm = WebSocketServerCommunicationService(version="v2")
    server_manager = RemotePduServiceServerManager("srv", pdu_config_path, offset_path, server_comm, uri)

    def boom(cid, pkt):
        raise RuntimeError("boom")

    server_manager.register_handler_pdu_data(boom)
    assert await server_manager.start_service(uri)

    client_comm = WebSocketCommunicationService(version="v2")
    client_buffer = CommunicationBuffer(PduChannelConfig(pdu_config_path))
    assert await client_comm.start_service(client_buffer, uri)
    await asyncio.sleep(0.1)

    data1 = b"1"
    await client_comm.send_data("test_client", 1, data1)
    await asyncio.sleep(0.1)
    assert server_manager.comm_buffer.get_buffer("test_client", "client_to_server") == data1

    data2 = b"2"
    await client_comm.send_data("test_client", 1, data2)
    await asyncio.sleep(0.1)
    assert server_manager.comm_buffer.get_buffer("test_client", "client_to_server") == data2

    await client_comm.stop_service()
    await server_manager.stop_service()
