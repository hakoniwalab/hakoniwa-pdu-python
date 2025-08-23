#!/usr/bin/python
# -*- coding: utf-8 -*-
import asyncio
import sys
import hakopy

from hakoniwa_pdu.rpc.shm.shm_pdu_service_client_manager import (
    ShmPduServiceClientManager,
)
from hakoniwa_pdu.rpc.auto_wire import make_protocol_client
from hakoniwa_pdu.rpc.protocol_client import ProtocolClientImmediate
from hakoniwa_pdu.pdu_msgs.hako_srv_msgs.pdu_pytype_AddTwoIntsRequest import (
    AddTwoIntsRequest,
)

# --- クライアント設定 ---
ASSET_NAME = 'NewClient'
CLIENT_NAME = 'Client_1'
SERVICE_NAME = 'Service/Add'
SERVICE_CONFIG_PATH = './examples/service.json'
# HAKO_BINARY_PATH環境変数から取得するか、デフォルト値を設定
OFFSET_PATH = 'tests/config/offset'
DELTA_TIME_USEC = 1000 * 1000

# グローバル変数としてマネージャとプロトコルを保持
pdu_manager: ShmPduServiceClientManager = None
protocol_client = None

async def run_rpc_client():
    """
    RPCクライアントのメインロジック
    """
    global protocol_client

    # 4. サーバーにRPCコールを実行
    try:
        # 最初の呼び出し
        req = AddTwoIntsRequest()
        req.a = 10
        req.b = 20
        print(f"\nCalling RPC: a={req.a}, b={req.b}")
        res = protocol_client.call(req)
        if res:
            print(f"Response received: sum={res.sum}")
        else:
            print("RPC call failed or timed out.")

        # 2回目の呼び出し
        if res:
            await asyncio.sleep(1) # 動作が分かりやすいように少し待つ
            req.a = res.sum
            req.b = 5
            print(f"\nCalling RPC: a={req.a}, b={req.b}")
            res = protocol_client.call(req)
            if res:
                print(f"Response received: sum={res.sum}")
            else:
                print("RPC call failed or timed out.")

    except Exception as e:
        print(f"An error occurred: {e}")
    
    # シミュレーションを続けるために無限ループ
    print("\nClient tasks finished. Idling...")
    while True:
        await asyncio.sleep(1)

def my_on_initialize(context):
    """
    Hakoniwaアセットの初期化コールバック
    """
    global pdu_manager, protocol_client
    print("Initializing PDU Service Manager for SHM...")

    protocol_client = make_protocol_client(
        pdu_manager=pdu_manager,
        service_name=SERVICE_NAME,
        client_name=CLIENT_NAME,
        srv="AddTwoInts",
        ProtocolClientClass=ProtocolClientImmediate,
    )
    # クライアントをサービスに登録
    print(f"Registering client '{CLIENT_NAME}' to service '{SERVICE_NAME}'...")
    if not protocol_client.register():
        print("Failed to register client. Exiting.")
        return 1
    
    print("Client registered successfully.")
    print("Initialization complete.")
    return 0

def my_on_manual_timing_control(context):
    """
    Hakoniwaアセットのメインループコールバック
    """
    try:
        asyncio.run(run_rpc_client())
    except KeyboardInterrupt:
        print("\nClient stopped by user.")
    return 0

def my_on_reset(context):
    return 0

# Hakoniwaへのコールバック関数を辞書として登録
my_callback = {
    'on_initialize': my_on_initialize,
    'on_simulation_step': None,
    'on_manual_timing_control': my_on_manual_timing_control,
    'on_reset': my_on_reset
}

def main():
    global pdu_manager
    """
    メインの実行関数
    """
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <pdu_config_path>")
        return 1
    
    pdu_config_path = sys.argv[1]

    # 1. PDUサービスマネージャを初期化
    pdu_manager = ShmPduServiceClientManager(
        asset_name=ASSET_NAME,
        pdu_config_path=pdu_config_path,
        offset_path=OFFSET_PATH
    )

    print(f"Registering asset: {ASSET_NAME}")
    # Hakoniwaにアセットを登録
    ret = hakopy.asset_register(ASSET_NAME, pdu_config_path, my_callback, DELTA_TIME_USEC, hakopy.HAKO_ASSET_MODEL_CONTROLLER)
    if not ret:
        print(f"ERROR: hako_asset_register() failed.")
        return 1
    
    # サービスを初期化
    if pdu_manager.initialize_services(SERVICE_CONFIG_PATH, DELTA_TIME_USEC) < 0:
        print(f"ERROR: hako_asset_service_initialize() failed.")
        return 1

    # シミュレーションを開始
    hakopy.start()
    print("Simulation finished.")

    return 0

if __name__ == "__main__":
    sys.exit(main())