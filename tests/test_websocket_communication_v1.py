import asyncio
import pytest
from hakoniwa_pdu.impl.communication_buffer import CommunicationBuffer
from hakoniwa_pdu.impl.websocket_communication_service import WebSocketCommunicationService
from hakoniwa_pdu.impl.websocket_server_communication_service import WebSocketServerCommunicationService
from hakoniwa_pdu.impl.pdu_channel_config import PduChannelConfig
from hakoniwa_pdu.impl.data_packet import DataPacket

@pytest.mark.asyncio
async def test_websocket_client_server_communication_v1():
    # 1. Setup
    uri = "ws://localhost:8766"
    pdu_config_path = "tests/pdu_config.json"
    pdu_channel_config = PduChannelConfig(pdu_config_path)

    server_comm = WebSocketServerCommunicationService(version="v1")
    client_comm = WebSocketCommunicationService(version="v1")
    server_buffer = CommunicationBuffer(pdu_channel_config)
    client_buffer = CommunicationBuffer(pdu_channel_config)

    # 2. Start Server
    assert await server_comm.start_service(server_buffer, uri) is True

    # 3. Start Client
    assert await client_comm.start_service(client_buffer, uri) is True
    assert client_comm.is_service_enabled() is True

    # Give some time for the connection to be established
    await asyncio.sleep(0.1)

    # 4. Client to Server Communication
    client_robot_name = "test_client"
    client_channel_id = 1
    client_pdu_data = b'client_to_server_test_v1'
    await client_comm.send_data(client_robot_name, client_channel_id, client_pdu_data)

    # 5. Verify Server received the data
    await asyncio.sleep(0.1) # wait for data to arrive
    server_received_data = server_buffer.get_buffer(client_robot_name, "client_to_server")
    assert server_received_data == client_pdu_data

    # 6. Server to Client Communication
    server_robot_name = "test_server"
    server_channel_id = 2
    server_pdu_data = b'server_to_client_test_v1'
    await server_comm.send_data(server_robot_name, server_channel_id, server_pdu_data)

    # 7. Verify Client received the data
    await asyncio.sleep(0.1) # wait for data to arrive
    client_received_data = client_buffer.get_buffer("test_server", "server_to_client")
    assert client_received_data == server_pdu_data

    # 8. Cleanup
    await client_comm.stop_service()
    await server_comm.stop_service()
