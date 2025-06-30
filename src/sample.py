import argparse
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

    # PDU読取登録
    if manager.declare_pdu_for_read('Drone', 'pos'):
        print(f"[OK] Declared PDU for READ: {args.robot}/{args.pdu}")
    else:
        print(f"[FAIL] Could not declare PDU for READ: {args.robot}/{args.pdu}")

if __name__ == "__main__":
    main()
