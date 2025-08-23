import asyncio
import os
import pytest
from hakoniwa_pdu.impl.websocket_communication_service import WebSocketCommunicationService
from hakoniwa_pdu.impl.websocket_server_communication_service import (
    WebSocketServerCommunicationService,
)
from hakoniwa_pdu.rpc.remote.remote_pdu_service_server_manager import (
    RemotePduServiceServerManager,
)
from hakoniwa_pdu.rpc.remote.remote_pdu_service_client_manager import (
    RemotePduServiceClientManager,
)
from hakoniwa_pdu.rpc.protocol_client import ProtocolClient
from hakoniwa_pdu.rpc.protocol_server import ProtocolServer
from hakoniwa_pdu.pdu_msgs.hako_srv_msgs.pdu_pytype_AddTwoIntsRequest import AddTwoIntsRequest
from hakoniwa_pdu.pdu_msgs.hako_srv_msgs.pdu_pytype_AddTwoIntsResponse import AddTwoIntsResponse
from hakoniwa_pdu.pdu_msgs.hako_srv_msgs.pdu_pytype_AddTwoIntsRequestPacket import AddTwoIntsRequestPacket
from hakoniwa_pdu.pdu_msgs.hako_srv_msgs.pdu_pytype_AddTwoIntsResponsePacket import AddTwoIntsResponsePacket
from hakoniwa_pdu.pdu_msgs.hako_srv_msgs.pdu_conv_AddTwoIntsRequestPacket import pdu_to_py_AddTwoIntsRequestPacket, py_to_pdu_AddTwoIntsRequestPacket
from hakoniwa_pdu.pdu_msgs.hako_srv_msgs.pdu_conv_AddTwoIntsResponsePacket import pdu_to_py_AddTwoIntsResponsePacket, py_to_pdu_AddTwoIntsResponsePacket

OFFSET_PATH = "./tests/config/offset"


@pytest.mark.asyncio
async def test_remote_rpc_call():
    # 1. Setup
    uri = "ws://localhost:8772"
    pdu_config_path = "tests/pdu_config.json"
    service_config_path = "examples/service.json"
    offset_path = OFFSET_PATH

    # Server setup
    server_comm = WebSocketServerCommunicationService(version="v2")
    server_pdu_manager = RemotePduServiceServerManager(
        "test_server", pdu_config_path, offset_path, server_comm, uri
    )
    server_pdu_manager.initialize_services(service_config_path, 1000 * 1000)
    protocol_server = ProtocolServer(
        service_name="Service/Add",
        max_clients=1,
        pdu_manager=server_pdu_manager,
        cls_req_packet=AddTwoIntsRequestPacket,
        req_encoder=py_to_pdu_AddTwoIntsRequestPacket,
        req_decoder=pdu_to_py_AddTwoIntsRequestPacket,
        cls_res_packet=AddTwoIntsResponsePacket,
        res_encoder=py_to_pdu_AddTwoIntsResponsePacket,
        res_decoder=pdu_to_py_AddTwoIntsResponsePacket
    )

    async def add_two_ints_handler(request: AddTwoIntsRequest) -> AddTwoIntsResponse:
        response = AddTwoIntsResponse()
        response.sum = request.a + request.b
        return response

    await protocol_server.start_service()
    server_task = asyncio.create_task(protocol_server.serve(add_two_ints_handler))

    # Client setup
    client_comm = WebSocketCommunicationService(version="v2")
    client_pdu_manager = RemotePduServiceClientManager(
        "test_client", pdu_config_path, offset_path, client_comm, uri
    )
    client_pdu_manager.initialize_services(service_config_path, 1000 * 1000)
    protocol_client = ProtocolClient(
        pdu_manager=client_pdu_manager,
        service_name="Service/Add",
        client_name="test_client",
        cls_req_packet=AddTwoIntsRequestPacket,
        req_encoder=py_to_pdu_AddTwoIntsRequestPacket,
        req_decoder=pdu_to_py_AddTwoIntsRequestPacket,
        cls_res_packet=AddTwoIntsResponsePacket,
        res_encoder=py_to_pdu_AddTwoIntsResponsePacket,
        res_decoder=pdu_to_py_AddTwoIntsResponsePacket
    )

    # 2. Register client
    assert await protocol_client.start_service(uri)
    assert await protocol_client.register()

    # 3. Make RPC call
    req = AddTwoIntsRequest()
    req.a = 10
    req.b = 20
    res = await protocol_client.call(req)

    # 4. Verify response
    assert res is not None
    assert res.sum == 30

    # 5. Cleanup
    server_task.cancel()
    await client_comm.stop_service()
    await server_comm.stop_service()
