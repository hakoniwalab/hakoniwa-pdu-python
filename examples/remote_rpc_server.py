#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""リモートRPCサーバの簡易サンプル."""
import asyncio
import argparse
import os

from hakoniwa_pdu.impl.websocket_server_communication_service import (
    WebSocketServerCommunicationService,
)
from hakoniwa_pdu.rpc.remote.remote_pdu_service_server_manager import (
    RemotePduServiceServerManager,
)
from hakoniwa_pdu.rpc.auto_wire import make_protocol_server
from hakoniwa_pdu.pdu_msgs.hako_srv_msgs.pdu_pytype_AddTwoIntsRequest import (
    AddTwoIntsRequest,
)
from hakoniwa_pdu.pdu_msgs.hako_srv_msgs.pdu_pytype_AddTwoIntsResponse import (
    AddTwoIntsResponse,
)

ASSET_NAME = "RemoteServer"
SERVICE_NAME = "Service/Add"
OFFSET_PATH = os.getenv("HAKO_BINARY_PATH", "/usr/local/hakoniwa/share/hakoniwa/offset")
DELTA_TIME_USEC = 1_000_000


async def add_handler(req: AddTwoIntsRequest) -> AddTwoIntsResponse:
    """加算サービスの実装."""
    res = AddTwoIntsResponse()
    res.sum = req.a + req.b
    return res


async def main() -> None:
    parser = argparse.ArgumentParser(description="Remote RPC server example")
    parser.add_argument("--uri", default="ws://localhost:8080", help="WebSocketサーバのURI")
    parser.add_argument("--pdu-config", default="examples/pdu_config.json")
    parser.add_argument("--service-config", default="examples/service.json")
    args = parser.parse_args()

    # WebSocketサーバ機能を持つコミュニケーションサービス
    comm = WebSocketServerCommunicationService(version="v2")
    manager = RemotePduServiceServerManager(
        asset_name=ASSET_NAME,
        pdu_config_path=args.pdu_config,
        offset_path=OFFSET_PATH,
        comm_service=comm,
        uri=args.uri,
    )
    manager.initialize_services(args.service_config, DELTA_TIME_USEC)

    server = make_protocol_server(
        pdu_manager=manager,
        service_name=SERVICE_NAME,
        srv="AddTwoInts",
        max_clients=1,
    )

    if not await server.start_service():
        print("サービス開始に失敗しました")
        return

    await server.serve(add_handler)


if __name__ == "__main__":
    asyncio.run(main())
