#!/usr/bin/python
# -*- coding: utf-8 -*-
import asyncio
import sys
import hakopy

# 新しいRPCコンポーネントをインポート
from hakoniwa_pdu.rpc.shm_pdu_service_manager import ShmPduServiceManager
from hakoniwa_pdu.rpc.client_protocol import ClientProtocol

# PDUの型定義とエンコーダ/デコーダをインポート
from hakoniwa_pdu.pdu_msgs.hako_srv_msgs.pdu_pytype_AddTwoIntsRequest import AddTwoIntsRequest
from hakoniwa_pdu.pdu_msgs.hako_srv_msgs.pdu_conv_AddTwoIntsRequestPacket import py_to_pdu_AddTwoIntsRequestPacket
from hakoniwa_pdu.pdu_msgs.hako_srv_msgs.pdu_conv_AddTwoIntsResponsePacket import pdu_to_py_AddTwoIntsResponsePacket

# --- クライアント設定 ---
ASSET_NAME = 'NewClient'
CLIENT_NAME = 'Client_1'
SERVICE_NAME = 'Service/Add'
SERVICE_CONFIG_PATH = './examples/service.json'
# HAKO_BINARY_PATH環境変数から取得するか、デフォルト値を設定
OFFSET_PATH = '/usr/local/lib/hakoniwa/hako_binary/offset'
DELTA_TIME_USEC = 1000 * 1000

# グローバル変数としてマネージャとプロトコルを保持
pdu_manager: ShmPduServiceManager = None
client_protocol: ClientProtocol = None

async def run_rpc_client():
    """
    RPCクライアントのメインロジック
    """
    global client_protocol
    print(f"Registering client '{CLIENT_NAME}' to service '{SERVICE_NAME}'...")
    # 3. クライアントをサービスに登録
    if not client_protocol.register():
        print("Failed to register client. Exiting.")
        return 1
    
    print("Client registered successfully.")

    # 4. サーバーにRPCコールを実行
    try:
        # 最初の呼び出し
        req = AddTwoIntsRequest()
        req.a = 10
        req.b = 20
        print(f"\nCalling RPC: a={req.a}, b={req.b}")
        res = await client_protocol.call(req)
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
            res = await client_protocol.call(req)
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
    global pdu_manager, client_protocol
    print("Initializing PDU Service Manager for SHM...")
    # 1. PDUサービスマネージャを初期化
    pdu_manager = ShmPduServiceManager(
        asset_name=ASSET_NAME,
        service_config_path=SERVICE_CONFIG_PATH,
        offset_path=OFFSET_PATH
    )

    # 2. クライアントプロトコルを初期化
    client_protocol = ClientProtocol(
        pdu_manager=pdu_manager,
        service_name=SERVICE_NAME,
        client_name=CLIENT_NAME,
        req_encoder=py_to_pdu_AddTwoIntsRequestPacket, # リクエストのエンコーダ
        res_decoder=pdu_to_py_AddTwoIntsResponsePacket   # レスポンスのデコーダ
    )
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
    """
    メインの実行関数
    """
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <pdu_config_path>")
        return 1
    
    pdu_config_path = sys.argv[1]

    print(f"Registering asset: {ASSET_NAME}")
    # Hakoniwaにアセットを登録
    ret = hakopy.asset_register(ASSET_NAME, pdu_config_path, my_callback, DELTA_TIME_USEC, hakopy.HAKO_ASSET_MODEL_CONTROLLER)
    if not ret:
        print(f"ERROR: hako_asset_register() failed.")
        return 1
    
    # サービスを初期化
    if hakopy.service_initialize(SERVICE_CONFIG_PATH) < 0:
        print(f"ERROR: hako_asset_service_initialize() failed.")
        return 1

    # シミュレーションを開始
    hakopy.start()
    print("Simulation finished.")

    return 0

if __name__ == "__main__":
    sys.exit(main())