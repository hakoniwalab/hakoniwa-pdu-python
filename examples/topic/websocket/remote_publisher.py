#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Remote topic publisher example."""
import asyncio
import argparse
import logging
import os
import sys

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

from hakoniwa_pdu.impl.websocket_server_communication_service import (
    WebSocketServerCommunicationService,
)
from hakoniwa_pdu.rpc.remote.remote_pdu_service_server_manager import (
    RemotePduServiceServerManager,
)
from hakoniwa_pdu.pdu_msgs.geometry_msgs.pdu_pytype_Twist import Twist
from hakoniwa_pdu.pdu_msgs.geometry_msgs.pdu_conv_Twist import py_to_pdu_Twist

ROBOT_NAME = "drone1"
TOPIC_NAME = "pos"
OFFSET_PATH = "tests/config/offset"
DELTA_TIME_USEC = 1_000_000

from hakoniwa_pdu.impl.data_packet import DataPacket


def handler_pdu_read_declaration(client_id: str, pkt: DataPacket) -> None:
    logging.info(
        f"PDU read declaration received: client_id={client_id}  "
        f"robot_name={pkt.meta_pdu.robot_name}  channel_id={pkt.meta_pdu.channel_id}"
    )

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
        logging.error("トピックサービスの開始に失敗しました")
        return

    channel_id = manager.comm_buffer.get_pdu_channel_id(ROBOT_NAME, TOPIC_NAME)
    count = 0
    while True:
        twist = Twist()
        twist.linear.x = count
        twist.angular.z = count
        pdu_data = py_to_pdu_Twist(twist)
        sent = await manager.publish_pdu(ROBOT_NAME, channel_id, pdu_data)
        logging.info(f"Published Twist #{count} to {sent} subscriber(s)")
        count += 1
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())