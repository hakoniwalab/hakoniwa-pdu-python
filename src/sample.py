import argparse
import asyncio
import sys
from pdu_manager import PduManager
from impl.websocket_communication_service import WebSocketCommunicationService

async def main():
    parser = argparse.ArgumentParser(description="Sample PDU Manager usage")
    parser.add_argument("--config", required=True, help="Path to PDU channel config JSON")
    parser.add_argument("--uri", required=True, help="WebSocket server URI")
    parser.add_argument("--read-time", type=int, default=5, help="Seconds to wait for PDU read")
    args = parser.parse_args()

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

    # 通信停止
    await manager.stop_service()
    print("[INFO] Communication service stopped.")


if __name__ == "__main__":
    asyncio.run(main())
