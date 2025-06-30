import argparse
import asyncio
import sys
import os
from pdu_manager import PduManager
from impl.websocket_communication_service import WebSocketCommunicationService
from impl.pdu_convertor import PduConvertor

async def main():
    parser = argparse.ArgumentParser(description="Sample PDU Manager usage")
    parser.add_argument("--config", required=True, help="Path to PDU channel config JSON")
    parser.add_argument("--uri", required=True, help="WebSocket server URI")
    parser.add_argument("--read-time", type=int, default=5, help="Seconds to wait for PDU read")
    args = parser.parse_args()

    hako_binary_path = os.getenv('HAKO_BINARY_PATH', '/usr/local/lib/hakoniwa/hako_binary/offset')
    pduConvertor = PduConvertor(hako_binary_path, args.config)

    # 通信サービス（WebSocket）を生成
    service = WebSocketCommunicationService()

    # PDUマネージャ初期化
    manager = PduManager()
    manager.initialize(config_path=args.config, comm_service=service)

    # 通信開始
    if not await manager.start_service(args.uri):
        print("[ERROR] Failed to start communication service.")
        sys.exit(1)

    # PDU読取登録
    robot_name = 'Drone'
    pdu_name = 'pos'
    if not await manager.declare_pdu_for_read(robot_name, pdu_name):
        print(f"[FAIL] Could not declare PDU for READ: {robot_name}/{pdu_name}")
        await manager.stop_service()
        sys.exit(1)

    print(f"[OK] Declared PDU for READ: {robot_name}/{pdu_name}")
    print(f"[INFO] Waiting {args.read_time} seconds to receive PDU data...")

    await asyncio.sleep(args.read_time)

    # PDU読取確認
    pdu_data = manager.read_pdu_raw_data(robot_name, pdu_name)
    if pdu_data:
        print(f"[RECV] Received PDU Data: {list(pdu_data)}")
    else:
        print("[INFO] No data received.")

    # debug twist data of pdu_data
    if pdu_data:
        try:
            json_data = pduConvertor.convert_binary_to_json(robot_name, pdu_name, pdu_data)
            print(f"[DEBUG] PDU JSON Data: {json_data}")
        except Exception as e:
            print(f"[ERROR] Failed to convert binary to JSON: {e}")

    # 通信停止
    await manager.stop_service()
    print("[INFO] Communication service stopped.")


if __name__ == "__main__":
    asyncio.run(main())
