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

ROBOT_NAME = "drone1"
TOPIC_NAME = "pos"
OFFSET_PATH = "tests/config/offset"
DELTA_TIME_USEC = 1_000_000

from hakoniwa_pdu.impl.data_packet import DataPacket 

def handler_pdu_read_declaration(pkt: DataPacket) -> None:
    print(f"[INFO] PDU read declaration received: robot_name={pkt.meta_pdu.robot_name}  channel_id={pkt.meta_pdu.channel_id}")

async def main() -> None:
    parser = argparse.ArgumentParser(description="Remote RPC server example")
    parser.add_argument("--uri", default="ws://localhost:8080", help="WebSocketサーバのURI")
    parser.add_argument("--pdu-config", default="examples/pdu_config.json")
    parser.add_argument("--service-config", default="examples/service.json")
    args = parser.parse_args()

    # WebSocketサーバ機能を持つコミュニケーションサービス
    comm = WebSocketServerCommunicationService(version="v2")
    manager = RemotePduServiceServerManager(
        asset_name="TEST_SERVER",
        pdu_config_path=args.pdu_config,
        offset_path=OFFSET_PATH,
        comm_service=comm,
        uri=args.uri,
    )
    manager.register_handler_pdu_for_read(handler_pdu_read_declaration)
    manager.initialize_services(args.service_config, DELTA_TIME_USEC)
    if not await manager.start_topic_service():
        print("トピックサービスの開始に失敗しました")
        return
    
    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
