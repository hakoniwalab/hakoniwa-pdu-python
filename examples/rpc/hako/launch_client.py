#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
import argparse
import os
import logging
import sys
from hakoniwa_pdu.rpc.codes import SystemControlOpCode

# Setup logging
if os.environ.get('HAKO_PDU_DEBUG') == '1':
    log_level = logging.DEBUG
else:
    log_level = logging.INFO

logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

from hakoniwa_pdu.impl.websocket_communication_service import WebSocketCommunicationService
from hakoniwa_pdu.rpc.remote.remote_pdu_service_client_manager import (
    RemotePduServiceClientManager,
)
from hakoniwa_pdu.rpc.auto_wire import make_protocol_client
from hakoniwa_pdu.rpc.protocol_client import ProtocolClientBlocking
from hakoniwa_pdu.pdu_msgs.hako_srv_msgs.pdu_pytype_SystemControlRequest import (
    SystemControlRequest,
)

ASSET_NAME = "HakoMcpServer"
CLIENT_NAME = "HakoMcpServer"
SERVICE_NAME = "Service/SystemControl"
OFFSET_PATH = "tests/config/offset"
DELTA_TIME_USEC = 1_000_000


async def main() -> None:
    parser = argparse.ArgumentParser(description="Remote RPC client example")
    parser.add_argument("--uri", default="ws://localhost:8080", help="WebSocketサーバのURI")
    parser.add_argument("--pdu-config", default="examples/rpc/hako/pdu_config.json")
    parser.add_argument("--service-config", default="examples/rpc/hako/service.json")
    args = parser.parse_args()

    comm = WebSocketCommunicationService(version="v2")
    manager = RemotePduServiceClientManager(
        asset_name=ASSET_NAME,
        pdu_config_path=args.pdu_config,
        offset_path=OFFSET_PATH,
        comm_service=comm,
        uri=args.uri,
    )
    manager.initialize_services(args.service_config, DELTA_TIME_USEC)

    client = make_protocol_client(
        pdu_manager=manager,
        service_name=SERVICE_NAME,
        client_name=CLIENT_NAME,
        srv="SystemControl",
        ProtocolClientClass=ProtocolClientBlocking,
    )

    if not await client.start_service(args.uri):
        print("通信サービス開始に失敗しました")
        return

    if not await client.register():
        print("クライアント登録に失敗しました")
        return

    req = SystemControlRequest()
    req.opcode = SystemControlOpCode.START
    res = await client.call(req, timeout_msec=1000)
    if res is None:
        print("RPC呼び出しに失敗しました")
        return
    print(f"レスポンス: {res}")


if __name__ == "__main__":
    asyncio.run(main())