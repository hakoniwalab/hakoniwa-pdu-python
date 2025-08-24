import asyncio
import contextlib
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
from hakoniwa_pdu.rpc.auto_wire import (
    make_protocol_client,
    make_protocol_server,
    make_protocol_clients,
    make_protocol_servers,
)
from hakoniwa_pdu.pdu_msgs.hako_srv_msgs.pdu_pytype_AddTwoIntsRequest import (
    AddTwoIntsRequest,
)
from hakoniwa_pdu.pdu_msgs.hako_srv_msgs.pdu_pytype_AddTwoIntsResponse import (
    AddTwoIntsResponse,
)
from hakoniwa_pdu.pdu_msgs.hako_srv_msgs.pdu_pytype_SystemControlRequest import (
    SystemControlRequest,
)
from hakoniwa_pdu.pdu_msgs.hako_srv_msgs.pdu_pytype_SystemControlResponse import (
    SystemControlResponse,
)

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
    protocol_server = make_protocol_server(
        pdu_manager=server_pdu_manager,
        service_name="Service/Add",
        srv="AddTwoInts",
        max_clients=1,
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
    protocol_client = make_protocol_client(
        pdu_manager=client_pdu_manager,
        service_name="Service/Add",
        client_name="test_client",
        srv="AddTwoInts",
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




@pytest.mark.asyncio
async def test_remote_multi_service_rpc_calls():
    uri = "ws://localhost:8772"
    pdu_config_path = "tests/pdu_config.json"
    service_config_path = "examples/service.json"
    offset_path = OFFSET_PATH

    # Server setup with two services
    server_comm = WebSocketServerCommunicationService(version="v2")
    server_pdu_manager = RemotePduServiceServerManager(
        "test_server", pdu_config_path, offset_path, server_comm, uri
    )
    server_pdu_manager.initialize_services(service_config_path, 1000 * 1000)
    protocol_server = make_protocol_servers(
        pdu_manager=server_pdu_manager,
        services=[
            {
                "service_name": "Service/Add",
                "srv": "AddTwoInts",
                "max_clients": 1,
            },
            {
                "service_name": "Service/SystemControl",
                "srv": "SystemControl",
                "max_clients": 1,
            },
        ],
    )

    async def add_handler(req: AddTwoIntsRequest) -> AddTwoIntsResponse:
        res = AddTwoIntsResponse()
        res.sum = req.a + req.b
        return res

    async def system_handler(req: SystemControlRequest) -> SystemControlResponse:
        res = SystemControlResponse()
        if req.opcode == 1:
            res.status_code = 0
            res.message = "OK"
        else:
            res.status_code = 1
            res.message = "NG"
        return res

    await protocol_server.start_services()
    server_task = asyncio.create_task(
        protocol_server.serve(
            {
                "Service/Add": add_handler,
                "Service/SystemControl": system_handler,
            }
        )
    )

    # Client setup with two services
    client_comm = WebSocketCommunicationService(version="v2")
    client_pdu_manager = RemotePduServiceClientManager(
        "test_client", pdu_config_path, offset_path, client_comm, uri
    )
    client_pdu_manager.initialize_services(service_config_path, 1000 * 1000)
    clients = make_protocol_clients(
        pdu_manager=client_pdu_manager,
        services=[
            {
                "service_name": "Service/Add",
                "client_name": "add_client",
                "srv": "AddTwoInts",
            },
            {
                "service_name": "Service/SystemControl",
                "client_name": "ctrl_client",
                "srv": "SystemControl",
            },
        ],
    )

    # Start communication and register both clients
    first_client = next(iter(clients.values()))
    assert await first_client.start_service(uri)
    for client in clients.values():
        assert await client.register()

    # Call AddTwoInts service
    add_req = AddTwoIntsRequest()
    add_req.a = 7
    add_req.b = 8
    add_res = await clients["Service/Add"].call(add_req)
    assert add_res is not None
    assert add_res.sum == 15

    # Call SystemControl service
    ctrl_req = SystemControlRequest()
    ctrl_req.opcode = 1
    ctrl_res = await clients["Service/SystemControl"].call(ctrl_req)
    assert ctrl_res is not None
    assert ctrl_res.status_code == 0
    assert ctrl_res.message == "OK"

    # Cleanup
    server_task.cancel()
    await client_comm.stop_service()
    await server_comm.stop_service()


@pytest.mark.asyncio
async def test_remote_system_control_rpc_call():
    uri = "ws://localhost:8772"
    pdu_config_path = "tests/pdu_config.json"
    service_config_path = "examples/service.json"
    offset_path = OFFSET_PATH

    server_comm = WebSocketServerCommunicationService(version="v2")
    server_pdu_manager = RemotePduServiceServerManager(
        "test_server", pdu_config_path, offset_path, server_comm, uri
    )
    server_pdu_manager.initialize_services(service_config_path, 1000 * 1000)
    protocol_server = make_protocol_server(
        pdu_manager=server_pdu_manager,
        service_name="Service/SystemControl",
        srv="SystemControl",
        max_clients=1,
    )

    async def handler(request: SystemControlRequest) -> SystemControlResponse:
        response = SystemControlResponse()
        if request.opcode == 1:
            response.status_code = 0
            response.message = "OK"
        else:
            response.status_code = 1
            response.message = "NG"
        return response

    await protocol_server.start_service()
    server_task = asyncio.create_task(protocol_server.serve(handler))

    client_comm = WebSocketCommunicationService(version="v2")
    client_pdu_manager = RemotePduServiceClientManager(
        "test_client", pdu_config_path, offset_path, client_comm, uri
    )
    client_pdu_manager.initialize_services(service_config_path, 1000 * 1000)
    protocol_client = make_protocol_client(
        pdu_manager=client_pdu_manager,
        service_name="Service/SystemControl",
        client_name="test_client",
        srv="SystemControl",
    )

    assert await protocol_client.start_service(uri)
    assert await protocol_client.register()

    req = SystemControlRequest()
    req.opcode = 1
    res = await protocol_client.call(req)

    assert res is not None
    assert res.status_code == 0
    assert res.message == "OK"

    server_task.cancel()
    await client_comm.stop_service()
    await server_comm.stop_service()


@pytest.mark.asyncio
async def test_remote_rpc_call_timeout():
    uri = "ws://localhost:8773"
    pdu_config_path = "tests/pdu_config.json"
    service_config_path = "examples/service.json"
    offset_path = OFFSET_PATH

    server_comm = WebSocketServerCommunicationService(version="v2")
    server_pdu_manager = RemotePduServiceServerManager(
        "test_server", pdu_config_path, offset_path, server_comm, uri
    )
    server_pdu_manager.initialize_services(service_config_path, 1000 * 1000)
    protocol_server = make_protocol_server(
        pdu_manager=server_pdu_manager,
        service_name="Service/Add",
        srv="AddTwoInts",
        max_clients=1,
    )
    await protocol_server.start_service()

    client_comm = WebSocketCommunicationService(version="v2")
    client_pdu_manager = RemotePduServiceClientManager(
        "test_client", pdu_config_path, offset_path, client_comm, uri
    )
    client_pdu_manager.initialize_services(service_config_path, 1000 * 1000)
    protocol_client = make_protocol_client(
        pdu_manager=client_pdu_manager,
        service_name="Service/Add",
        client_name="test_client",
        srv="AddTwoInts",
    )

    assert await protocol_client.start_service(uri)
    assert await protocol_client.register()

    req = AddTwoIntsRequest()
    req.a = 1
    req.b = 2

    pdu_data = protocol_client._create_request_packet(req, 0.01)
    assert await client_pdu_manager.call_request(
        protocol_client.client_id, pdu_data, timeout_msec=100
    )

    event = client_pdu_manager.CLIENT_API_EVENT_NONE
    while event == client_pdu_manager.CLIENT_API_EVENT_NONE:
        event = client_pdu_manager.poll_response(protocol_client.client_id)
        await asyncio.sleep(0.05)
    assert client_pdu_manager.is_client_event_timeout(event)

    await client_comm.stop_service()
    await server_comm.stop_service()


@pytest.mark.asyncio
async def test_remote_rpc_cancel_not_implemented():
    uri = "ws://localhost:8774"
    pdu_config_path = "tests/pdu_config.json"
    service_config_path = "examples/service.json"
    offset_path = OFFSET_PATH

    server_comm = WebSocketServerCommunicationService(version="v2")
    server_pdu_manager = RemotePduServiceServerManager(
        "test_server", pdu_config_path, offset_path, server_comm, uri
    )
    server_pdu_manager.initialize_services(service_config_path, 1000 * 1000)
    protocol_server = make_protocol_server(
        pdu_manager=server_pdu_manager,
        service_name="Service/Add",
        srv="AddTwoInts",
        max_clients=1,
    )
    await protocol_server.start_service()

    client_comm = WebSocketCommunicationService(version="v2")
    client_pdu_manager = RemotePduServiceClientManager(
        "test_client", pdu_config_path, offset_path, client_comm, uri
    )
    client_pdu_manager.initialize_services(service_config_path, 1000 * 1000)
    protocol_client = make_protocol_client(
        pdu_manager=client_pdu_manager,
        service_name="Service/Add",
        client_name="test_client",
        srv="AddTwoInts",
    )

    assert await protocol_client.start_service(uri)
    assert await protocol_client.register()

    with pytest.raises(NotImplementedError):
        await protocol_client.cancel()

    await client_comm.stop_service()
    await server_comm.stop_service()
