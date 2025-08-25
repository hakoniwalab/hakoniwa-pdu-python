import asyncio
import pytest
from hakoniwa_pdu.impl.communication_buffer import CommunicationBuffer
from hakoniwa_pdu.impl.websocket_communication_service import WebSocketCommunicationService
from hakoniwa_pdu.impl.websocket_server_communication_service import WebSocketServerCommunicationService
from hakoniwa_pdu.impl.pdu_channel_config import PduChannelConfig
from hakoniwa_pdu.impl.data_packet import DataPacket, DECLARE_PDU_FOR_READ, DECLARE_PDU_FOR_WRITE, REGISTER_RPC_CLIENT

@pytest.mark.asyncio
async def test_websocket_client_server_communication_v2():
    # 1. Setup
    uri = "ws://localhost:8765"
    pdu_config_path = "tests/pdu_config.json"
    pdu_channel_config = PduChannelConfig(pdu_config_path)

    server_comm = WebSocketServerCommunicationService(version="v2")
    client_comm = WebSocketCommunicationService(version="v2")
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
    client_pdu_data = b'client_to_server_test'
    await client_comm.send_data(client_robot_name, client_channel_id, client_pdu_data)

    # 5. Verify Server received the data
    await asyncio.sleep(0.1) # wait for data to arrive
    server_received_data = server_buffer.get_buffer(client_robot_name, "client_to_server")
    assert server_received_data == client_pdu_data

    # 6. Server to Client Communication
    server_robot_name = "test_server"
    server_channel_id = 2
    server_pdu_data = b'server_to_client_test'
    await server_comm.send_data(server_robot_name, server_channel_id, server_pdu_data)

    # 7. Verify Client received the data
    await asyncio.sleep(0.1) # wait for data to arrive
    client_received_data = client_buffer.get_buffer("test_server", "server_to_client")
    assert client_received_data == server_pdu_data

    # 8. Cleanup
    await client_comm.stop_service()
    await server_comm.stop_service()


@pytest.mark.asyncio
async def test_websocket_client_disconnect_and_reconnect_v2():
    uri = "ws://localhost:8771"
    pdu_config_path = "tests/pdu_config.json"
    pdu_channel_config = PduChannelConfig(pdu_config_path)

    server_comm = WebSocketServerCommunicationService(version="v2")
    server_buffer = CommunicationBuffer(pdu_channel_config)
    assert await server_comm.start_service(server_buffer, uri) is True

    first_client = WebSocketCommunicationService(version="v2")
    first_buffer = CommunicationBuffer(pdu_channel_config)
    assert await first_client.start_service(first_buffer, uri) is True
    await asyncio.sleep(0.1)
    assert len(server_comm.clients) == 1

    await first_client.stop_service()
    await asyncio.sleep(0.1)
    assert len(server_comm.clients) == 0

    second_client = WebSocketCommunicationService(version="v2")
    second_buffer = CommunicationBuffer(pdu_channel_config)
    assert await second_client.start_service(second_buffer, uri) is True
    await asyncio.sleep(0.1)
    assert len(server_comm.clients) == 1

    await second_client.stop_service()
    await server_comm.stop_service()

@pytest.mark.asyncio
async def test_websocket_declare_pdu_for_read_v2():
    # 1. Setup
    uri = "ws://localhost:8767"
    pdu_config_path = "tests/pdu_config.json"
    pdu_channel_config = PduChannelConfig(pdu_config_path)

    server_comm = WebSocketServerCommunicationService(version="v2")
    client_comm = WebSocketCommunicationService(version="v2")
    server_buffer = CommunicationBuffer(pdu_channel_config)
    client_buffer = CommunicationBuffer(pdu_channel_config)

    received_packet = None
    async def server_event_handler(packet, client_id):
        nonlocal received_packet
        received_packet = packet

    server_comm.register_event_handler(server_event_handler)

    # 2. Start Server and Client
    assert await server_comm.start_service(server_buffer, uri) is True
    assert await client_comm.start_service(client_buffer, uri) is True

    await asyncio.sleep(0.1)

    # 3. Send DECLARE_PDU_FOR_READ packet
    client_robot_name = "test_client"
    client_channel_id = 1
    packet_to_send = DataPacket(client_robot_name, client_channel_id, b'')
    encoded_packet = packet_to_send.encode("v2", meta_request_type=DECLARE_PDU_FOR_READ)
    await client_comm.send_binary(encoded_packet)

    # 4. Verify server received the packet
    await asyncio.sleep(0.1)
    assert received_packet is not None
    assert received_packet.get_robot_name() == client_robot_name
    assert received_packet.get_channel_id() == client_channel_id
    assert received_packet.meta_pdu.meta_request_type == DECLARE_PDU_FOR_READ

    # 5. Cleanup
    await client_comm.stop_service()
    await server_comm.stop_service()

@pytest.mark.asyncio
async def test_websocket_declare_pdu_for_write_v2():
    # 1. Setup
    uri = "ws://localhost:8768"
    pdu_config_path = "tests/pdu_config.json"
    pdu_channel_config = PduChannelConfig(pdu_config_path)

    server_comm = WebSocketServerCommunicationService(version="v2")
    client_comm = WebSocketCommunicationService(version="v2")
    server_buffer = CommunicationBuffer(pdu_channel_config)
    client_buffer = CommunicationBuffer(pdu_channel_config)

    received_packet = None
    async def server_event_handler(packet, client_id):
        nonlocal received_packet
        received_packet = packet

    server_comm.register_event_handler(server_event_handler)

    # 2. Start Server and Client
    assert await server_comm.start_service(server_buffer, uri) is True
    assert await client_comm.start_service(client_buffer, uri) is True

    await asyncio.sleep(0.1)

    # 3. Send DECLARE_PDU_FOR_WRITE packet
    client_robot_name = "test_client"
    client_channel_id = 1
    packet_to_send = DataPacket(client_robot_name, client_channel_id, b'')
    encoded_packet = packet_to_send.encode("v2", meta_request_type=DECLARE_PDU_FOR_WRITE)
    await client_comm.send_binary(encoded_packet)

    # 4. Verify server received the packet
    await asyncio.sleep(0.1)
    assert received_packet is not None
    assert received_packet.get_robot_name() == client_robot_name
    assert received_packet.get_channel_id() == client_channel_id
    assert received_packet.meta_pdu.meta_request_type == DECLARE_PDU_FOR_WRITE

    # 5. Cleanup
    await client_comm.stop_service()
    await server_comm.stop_service()

@pytest.mark.asyncio
async def test_websocket_register_rpc_client_v2():
    # 1. Setup
    uri = "ws://localhost:8769"
    pdu_config_path = "tests/pdu_config.json"
    pdu_channel_config = PduChannelConfig(pdu_config_path)

    server_comm = WebSocketServerCommunicationService(version="v2")
    client_comm = WebSocketCommunicationService(version="v2")
    server_buffer = CommunicationBuffer(pdu_channel_config)
    client_buffer = CommunicationBuffer(pdu_channel_config)

    received_packet = None
    async def server_event_handler(packet, client_id):
        nonlocal received_packet
        received_packet = packet

    server_comm.register_event_handler(server_event_handler)

    # 2. Start Server and Client
    assert await server_comm.start_service(server_buffer, uri) is True
    assert await client_comm.start_service(client_buffer, uri) is True

    await asyncio.sleep(0.1)

    # 3. Send REGISTER_RPC_CLIENT packet
    client_robot_name = "test_client"
    client_channel_id = 1
    packet_to_send = DataPacket(client_robot_name, client_channel_id, b'')
    encoded_packet = packet_to_send.encode("v2", meta_request_type=REGISTER_RPC_CLIENT)
    await client_comm.send_binary(encoded_packet)

    # 4. Verify server received the packet
    await asyncio.sleep(0.1)
    assert received_packet is not None
    assert received_packet.get_robot_name() == client_robot_name
    assert received_packet.get_channel_id() == client_channel_id
    assert received_packet.meta_pdu.meta_request_type == REGISTER_RPC_CLIENT

    # 5. Cleanup
    await client_comm.stop_service()
    await server_comm.stop_service()
