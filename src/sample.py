import argparse
import time
from pdu_manager import PduManager
from impl.websocket_communication_service import WebSocketCommunicationService

def main():
    parser = argparse.ArgumentParser(description="Sample PDU Manager usage")
    parser.add_argument("--config", required=True, help="Path to PDU channel config JSON")
    parser.add_argument("--uri", required=True, help="WebSocket server URI")
    args = parser.parse_args()

    # 通信サービス（WebSocket）を生成
    service = WebSocketCommunicationService()

    # PDUマネージャ初期化
    manager = PduManager()
    manager.initialize(config_path=args.config, comm_service=service)

    # 通信開始
    if not manager.start_service(args.uri):
        print("[ERROR] Failed to start communication service.")
        return
    
    while True:
        if manager.is_service_enabled():
            print("[INFO] Communication service is running.")
            break
        else:
            print("[INFO] Waiting for communication service to start...")
            time.sleep(1)

    # PDU読取登録
    robot_name = 'Drone'
    pdu_name = 'pos'
    if manager.declare_pdu_for_read('Drone', 'pos'):
        print(f"[OK] Declared PDU for READ: {robot_name}/{pdu_name}")
    else:
        print(f"[FAIL] Could not declare PDU for READ: {robot_name}/{pdu_name}")

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
