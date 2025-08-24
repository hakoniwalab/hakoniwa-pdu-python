#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""リモートRPCクライアントの簡易サンプル."""
import asyncio
import argparse
import os

from hakoniwa_pdu.impl.websocket_communication_service import WebSocketCommunicationService
from hakoniwa_pdu.rpc.remote.remote_pdu_service_client_manager import (
    RemotePduServiceClientManager,
)

ASSET_NAME = "TEST_SUBSCRIBER"
OFFSET_PATH = "tests/config/offset"
DELTA_TIME_USEC = 1_000_000


async def main() -> None:
    parser = argparse.ArgumentParser(description="Remote RPC client example")
    parser.add_argument("--uri", default="ws://localhost:8080", help="WebSocketサーバのURI")
    parser.add_argument("--pdu-config", default="examples/pdu_config.json")
    parser.add_argument("--service-config", default="examples/service.json")
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
    if not await manager.start_client_service():
        print("通信サービス開始に失敗しました")
        return
    if not await manager.declare_pdu_for_read("drone1", "pos"):
        print("PDUの宣言に失敗しました")
        return
    print("PDUの宣言に成功しました")

    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
