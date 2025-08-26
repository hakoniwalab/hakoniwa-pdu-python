#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
import argparse
import os
import logging
import sys
from hakoniwa_pdu.rpc.codes import SystemControlOpCode, SystemControlStatusCode

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
from hakoniwa_pdu.rpc.auto_wire import make_protocol_server
from hakoniwa_pdu.rpc.protocol_server import ProtocolServerBlocking
from hakoniwa_pdu.pdu_msgs.hako_srv_msgs.pdu_pytype_SystemControlRequest import (
    SystemControlRequest,
)
from hakoniwa_pdu.pdu_msgs.hako_srv_msgs.pdu_pytype_SystemControlResponse import (
    SystemControlResponse,
)

ASSET_NAME = "LaunchServer"
SERVICE_NAME = "Service/SystemControl"
OFFSET_PATH = "tests/config/offset"
DELTA_TIME_USEC = 1_000_000


async def system_control_handler(req: SystemControlRequest) -> SystemControlResponse:
    """システム制御サービスの実装."""
    res = SystemControlResponse()
    match req.opcode:
        case SystemControlOpCode.START:
            logging.info("SystemControlOpCode: START")
        case SystemControlOpCode.STOP:
            logging.info("SystemControlOpCode: STOP")
        case SystemControlOpCode.RESET:
            logging.info("SystemControlOpCode: RESET")
        case SystemControlOpCode.TERMINATE:
            logging.info("SystemControlOpCode: TERMINATE")
        case SystemControlOpCode.STATUS:
            logging.info("SystemControlOpCode: STATUS")
        case _:
            logging.warning(f"Unknown opcode: {req.opcode}")
    res.status_code = SystemControlStatusCode.OK
    res.message = "OK"
    # ここにシステム制御のロジックを実装
    logging.info(f"SystemControl called: {req}")
    return res


async def main() -> None:
    parser = argparse.ArgumentParser(description="Remote RPC server example")
    parser.add_argument("--uri", default="ws://localhost:8080", help="WebSocketサーバのURI")
    parser.add_argument("--pdu-config", default="examples/rpc/hako/pdu_config.json")
    parser.add_argument("--service-config", default="examples/rpc/hako/service.json")
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
        srv="SystemControl",
        max_clients=1,
        ProtocolServerClass=ProtocolServerBlocking,
    )

    if not await server.start_service():
        logging.error("サービス開始に失敗しました")
        return

    await server.serve(system_control_handler)


if __name__ == "__main__":
    asyncio.run(main())